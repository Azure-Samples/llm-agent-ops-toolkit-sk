import os
import sys
import json
import asyncio
from uuid import uuid4
from dotenv import load_dotenv
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from exp_src.model.batch_output import BatchOutput

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(override=True)

# The following imports having dependencies on the environment variables
from src.mysql.execution_env import SqlEnv
from src.groupchat.state_flow_chat import get_chat_client

sql_executor_env = SqlEnv.get_sql_executor_env_from_environment()

async def main(batch_jsonl_input_file: str, batch_output_path: str, experiment_name: str):
    thread_id = str(uuid4())
    input_data = []
    output_data = []
    all_roles = set()
    with open(batch_jsonl_input_file, "r") as f:
        for line in f:
            input_data.append(json.loads(line))
    print(f"Loaded {len(input_data)} input data from {batch_jsonl_input_file}")
    try:
        index = 0
        for data in input_data:
            parent_id = str(uuid4())
            conversation_history = ""
            chat = get_chat_client(sql_executor_env)
            input_query = data["input"]
            print(f"{index} - Query # {AuthorRole.USER}: '{input_query}'", end=" .... ")

            query_with_init_thought = sql_executor_env.attach_init_observation(
                input_query
            )
            await chat.add_chat_message(
                ChatMessageContent(
                    role=AuthorRole.USER, content=query_with_init_thought
                )
            )

            async for content in chat.invoke():
                # print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
                output = f"{content.role.upper()} - {content.name or '*'}: {content.content}"
                conversation_history += f"{output}\n"
                output_data.append(
                    BatchOutput(
                        experiment=experiment_name,
                        role = content.name,
                        name = content.name,
                        threadId = thread_id,
                        parentId = parent_id,
                        input = input_query,
                        output = output,
                        conversation_history = conversation_history
                    )
                )
                all_roles.add(content.name)
            print("done.")
            index += 1
    finally:
        for role in all_roles:
            output_file = os.path.join(batch_output_path, f"{role.lower()}.jsonl")
            with open(output_file, "w") as f:
                for output in output_data:
                    if output.role == role:
                        f.write(json.dumps(output.to_dict_without_role()) + "\n")
            print(f"Output data for {role} saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError(
            "Please provide a JSONL file with the input data and output path, usage: python app_experiment_batch.py <input_data_file> <output_path> <experiment_name>"
        )
    batch_jsonl_input_file = sys.argv[1]
    batch_output_path = sys.argv[2]
    experiment_name = sys.argv[3]
    if not os.path.exists(batch_jsonl_input_file):
        raise FileNotFoundError(f"Input data file {batch_jsonl_input_file} not found")
    if not os.path.exists(batch_output_path):
        os.makedirs(batch_output_path)
    asyncio.run(main(batch_jsonl_input_file, batch_output_path, experiment_name))
