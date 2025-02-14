import os
import sys
from dotenv import load_dotenv
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.input_widget import TextInput
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents import ImageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(override=True)

# The following imports having dependencies on the environment variables
from src.mysql.execution_env import SqlEnv
from src.groupchat.state_flow_chat import get_chat_client
from exp_src.persistence.database_setup import DataPersistence
from exp_src.customization.actions import CustomActions

sql_executor_env = SqlEnv.get_sql_executor_env_from_environment()
data_persistence = DataPersistence(enable_storage_provider=False)


@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(
        conninfo=data_persistence.get_connection_url_async(),
        storage_provider=data_persistence.get_storage_provider(),
    )


@cl.password_auth_callback
def password_auth_callback(username: str, password: str) -> bool:
    if (username == os.environ["CHAINLIT_USERNAME"]) and (
        password == os.environ["CHAINLIT_PASSWORD"]
    ):
        return cl.User(
            identifier=username,
            metadata={"role": os.environ["CHAINLIT_ROLE"], "provider": "credentials"},
        )
    return None


@cl.action_callback("thumbs_up_action")
async def thumbs_up_action_callback(action: cl.Action) -> None:
    await CustomActions.thumbs_up_down_action_handler(
        message_id=action.payload["message_id"],
        thread_id=action.payload["thread_id"],
        value=action.payload["value"],
        data_layer=get_data_layer(),
    )


@cl.action_callback("thumbs_down_action")
async def thumbs_down_action_callback(action: cl.Action) -> None:
    await CustomActions.thumbs_up_down_action_handler(
        message_id=action.payload["message_id"],
        thread_id=action.payload["thread_id"],
        value=action.payload["value"],
        data_layer=get_data_layer(),
    )


@cl.on_settings_update
async def setting_update(settings):
    cl.context.session.chat_settings = settings


@cl.on_chat_start
async def start_chat():
    print("=================Chat started================")
    sql_executor_env.connect()
    global chat
    chat = get_chat_client(sql_executor_env)
    await cl.ChatSettings(
        [
            TextInput(
                id="experiment",
                label="Experiment",
                placeholder="Mention Experiment Name",
                initial="SQL Copilot Experiment",
                tooltip="Name of the experiment",
            )
        ]
    ).send()


async def run_team(query: str, image_content: ImageContent):
    query_with_init_thought = sql_executor_env.attach_init_observation(query)
    if image_content:
        await chat.add_chat_message(
            ChatMessageContent(role=AuthorRole.USER, items=[TextContent(text=query_with_init_thought), image_content])
        )
    else:
        await chat.add_chat_message(
            ChatMessageContent(role=AuthorRole.USER, content=query_with_init_thought)
        )
    cl_msg = cl.Message(
        content=f"{AuthorRole.USER.upper()}: init: {query_with_init_thought}",
        author=AuthorRole.USER,
    )
    await cl_msg.send()

    async for content in chat.invoke():
        message_metadata = {
            "experiment": cl.context.session.chat_settings.get("experiment", None)
        }
        cl_msg = cl.Message(
            content=f"{content.role.upper()} - {content.name or '*'}: {content.content}",
            author=content.name,
            metadata=message_metadata,
        )
        sent_message = await cl_msg.send()
        if not chat.is_complete:
            current_thread_id = cl.context.current_run.thread_id
            custom_actions = CustomActions(
                message_id=sent_message.id, thread_id=current_thread_id
            )
            cl_msg.actions = [
                custom_actions.get_thumbs_up_action(),
                custom_actions.get_thumbs_down_action(),
            ]
            await cl_msg.update()


@cl.on_message
async def run_chat(message: cl.Message):
    if message.elements:
        if len(message.elements) > 1:
            await cl.Message(content="Please provide only one image at a time.").send()
            return
        image = [file for file in message.elements if "image" in file.mime][0]
        image_content = ImageContent.from_image_file(image.path)
        await run_team(message.content, image_content)
    else:
        await run_team(message.content, None)


@cl.on_chat_end
async def end_chat():
    print("=================Chat ended==================")
    chat.is_complete = True
    sql_executor_env.close()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Simple Query",
            message="What is the total amount of sales so far?",
        ),
        cl.Starter(
            label="Simple Query with Join",
            message="List all product line along the number of orders placed for each product line.",
        ),
        cl.Starter(
            label="Complex Query with 3 joins",
            message="How many employees are placing orders?",
        ),
        cl.Starter(
            label="Irrelevant Query",
            message="What is latest stock price of Microsoft?",
        ),
    ]
