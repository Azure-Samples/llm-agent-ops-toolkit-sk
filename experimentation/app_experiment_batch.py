import os
import sys
import json
import asyncio
from uuid import uuid4
from dotenv import load_dotenv
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from exp_src.model.batch_output import BatchOutput, AgentInvokingTrajectory, AgentInvokingData

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
    agent_invoking_trajectory = []
    all_roles = set()
    with open(batch_jsonl_input_file, "r") as f:
        for line in f:
            input_data.append(json.loads(line))
    print(f"Loaded {len(input_data)} input data from {batch_jsonl_input_file}")
    try:
        index = 0
        for data in input_data:
            parent_id = str(uuid4())
            agent_selections = []
            chat = get_chat_client(sql_executor_env)
            input_query = data["input"]
            final_output = ""
            print(f"{index} - Query # {AuthorRole.USER}: '{input_query}'", end=" .... ")

            query_with_init_thought = sql_executor_env.attach_init_observation(
                input_query
            )
            await chat.add_chat_message(
                ChatMessageContent(
                    role=AuthorRole.USER, content=query_with_init_thought
                )
            )
            conversation_history = f"{AuthorRole.USER.upper()} - user: {query_with_init_thought}\n"

            async for content in chat.invoke():
                output = f"{content.role.upper()} - {content.name or '*'}: {content.content}"
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
                agent_selections.append(
                    AgentInvokingData(
                        name=content.name,
                        conversation_history=conversation_history
                    )
                )
                conversation_history += f"{output}\n"
                final_output = str(content.content)
            agent_invoking_trajectory.append(
                AgentInvokingTrajectory(
                    experiment=experiment_name,
                    threadId=thread_id,
                    input=input_query,
                    final_output=final_output,
                    agent_selections=agent_selections
                )
            )
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
        if len(agent_invoking_trajectory) > 0:
            output_file = os.path.join(batch_output_path, "all_agents.jsonl")
            with open(output_file, "w") as f:
                for trajectory in agent_invoking_trajectory:
                    f.write(json.dumps(trajectory.to_dict()) + "\n")
                    # If we want to flatten the agent selections into multiple lines
                    # for item in trajectory.to_flattened_dict():
                    #     f.write(json.dumps(item) + "\n")
            print(f"Agent invoking trajectory saved to {output_file}")


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
