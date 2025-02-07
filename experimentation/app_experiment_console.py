import os
import sys
import asyncio
from dotenv import load_dotenv
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(override=True)

# The following imports having dependencies on the environment variables
from src.mysql.execution_env import SqlEnv
from src.groupchat.state_flow_chat import get_chat_client

sql_executor_env = SqlEnv.get_sql_executor_env_from_environment()


async def main():
    try:
        chat = get_chat_client(sql_executor_env)
        while True:
            input_query = "Total order value"
            input_query = input(
                "Enter your message (type 'exit' to quit or 'reset' to reset the chat history and start over): "
            )
            if input_query == "exit":
                break
            if input_query == "reset":
                chat = get_chat_client(sql_executor_env)
                continue

            query_with_init_thought = sql_executor_env.attach_init_observation(
                input_query
            )
            await chat.add_chat_message(
                ChatMessageContent(
                    role=AuthorRole.USER, content=query_with_init_thought
                )
            )
            print(f"# {AuthorRole.USER}: '{input_query}'")

            async for content in chat.invoke():
                print(f"# {content.role} - {content.name or '*'}: '{content.content}'")

            print(f"# IS COMPLETE: {chat.is_complete}")
            await chat.add_chat_message(
                ChatMessageContent(role=AuthorRole.ASSISTANT, content=content.content)
            )
            chat.is_complete = False
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())
