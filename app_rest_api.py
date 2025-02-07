import os
import logging
import uvicorn
from dotenv import load_dotenv
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.utils.constants import Constants
from src.logging.telemetry import set_up_logging, set_up_tracing, set_up_metrics

if os.path.exists(".env"):
    load_dotenv(override=True)
else:
    raise FileNotFoundError("The .env file is missing")

application_insights_key = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
if application_insights_key:
    set_up_logging(application_insights_key)
    set_up_tracing(application_insights_key)
    set_up_metrics(application_insights_key)

# The following imports having dependencies on the environment variables
from src.mysql.execution_env import SqlEnv
from src.groupchat.state_flow_chat import get_chat_client

app = FastAPI()
logger: logging.Logger = logging.getLogger("semantic_kernel")
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("semantic_kernel")
sql_executor_env = SqlEnv.get_sql_executor_env_from_environment()

# OpenTelemetry setup
if application_insights_key:
    FastAPIInstrumentor().instrument_app(app)
    span_processor = BatchSpanProcessor(
        AzureMonitorTraceExporter.from_connection_string(application_insights_key)
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

if os.getenv("IS_DEVELOPMENT", "False").lower() == "true":
    logging.basicConfig(level=logging.INFO)


@app.get("/")
async def home() -> dict:
    """Home page of the API"""
    return {
        "MySQL Copilot": "Welcome to the MySQL Copilot API!",
        "API Documentation": "/docs",
    }


@app.get("/chat")
async def chat(query: str) -> dict:
    """API endpoint to interact with the chatbot"""
    try:
        logger.info(f"Query: {query}")
        chat = get_chat_client(sql_executor_env)
        query_with_init_thought = sql_executor_env.attach_init_observation(query)
        await chat.add_chat_message(
            ChatMessageContent(role=AuthorRole.USER, content=query_with_init_thought)
        )
        response = []
        async for content in chat.invoke():
            response.append(
                {
                    "role": content.role,
                    "name": content.name,
                    "content": content.content,
                    "finish_reason": content.finish_reason,
                }
            )
            logger.info(
                f"# {content.role} - {content.name or '*'}: '{content.content}'"
            )
        final_response = (
            response[-1]
            if len(response) > 0
            else {"is_error": "true", "content": Constants.default_response}
        )
        final_response["is_error"] = "false"
        if (
            not final_response.get("finish_reason")
            or final_response.get("finish_reason") != "stop"
        ):
            final_response["is_error"] = "true"
            final_response["content"] = Constants.default_response
            return final_response
        final_response["content"] = (
            final_response["content"]
            .replace(Constants.observation_identifier, "")
            .strip()
        )
        logger.info(f"Final response: {final_response}")
        return final_response
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", e)
        logger.exception(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal Server Error, check the logs for more details"},
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)
