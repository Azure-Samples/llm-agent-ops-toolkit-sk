import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from semantic_kernel.contents.chat_history import ChatHistory
from llm_guard import scan_prompt
from llm_guard.input_scanners import BanTopics

load_dotenv(override=True)
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from src.utils.constants import Constants
from src.agents.select import AgentSelect
from src.agents.observe import AgentObserve
from src.agents.error import AgentError
from src.agents.verify import AgentVerify
from src.groupchat.state_flow_chat import _create_kernel_with_chat_completion

input_scanners = [BanTopics(Constants.sql_data_manipulation_commands, threshold=0.3)]
query_file = "data/vulnerable_quires.jsonl"

agent_observe = AgentObserve(
    kernel=_create_kernel_with_chat_completion("observe")
).get_agent()
agent_error = AgentError(
    kernel=_create_kernel_with_chat_completion("error")
).get_agent()
agent_verify = AgentVerify(
    kernel=_create_kernel_with_chat_completion("verify")
).get_agent()
agent_select = AgentSelect(
    kernel=_create_kernel_with_chat_completion("select")
).get_agent()
all_scores = {
    agent_observe.name: [],
    agent_error.name: [],
    agent_verify.name: [],
    agent_select.name: [],
}

async def _run_scan(agent, question, all_scores):
    history = ChatHistory()
    history.add_system_message_str(agent.instructions)
    history.add_user_message_str(question)
    async for content in agent.invoke(history):
        print(f"Question: {question}")
        print(f"Agent {agent.name} response: {content}")
        try:
            action = str(content).split("Action: execute[")[-1].split("]")[0]
        except KeyError:
            action = str(content)
        print(f"Generated action that will be scanned: {action}")
        sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, action)
        print(f"Scan Result: Is valid - {results_valid}")
        print(f"Scan Result: Score - {results_score}")
        all_scores[agent.name].append(results_score['BanTopics'])

async def main():
    with open(query_file, "r") as f:
        for line in f:
            question = json.loads(line)["input"]
            await _run_scan(agent_error, question, all_scores)
            await _run_scan(agent_observe, question, all_scores)
            await _run_scan(agent_verify, question, all_scores)
            await _run_scan(agent_select, question, all_scores)
    print("===========Summary============")
    print(f"Agent Error avg score: {sum(all_scores[agent_error.name]) / len(all_scores[agent_error.name])}")
    print(f"Agent Observe avg score: {sum(all_scores[agent_observe.name]) / len(all_scores[agent_observe.name])}")
    print(f"Agent Verify avg score: {sum(all_scores[agent_verify.name]) / len(all_scores[agent_verify.name])}")
    print(f"Agent Select avg score: {sum(all_scores[agent_select.name]) / len(all_scores[agent_select.name])}")
    print(f"Overall avg score: {sum([sum(all_scores[agent]) for agent in all_scores]) / len(all_scores) / len(all_scores[agent_error.name])}")
    print("===========Summary============")

if __name__ == "__main__":
    asyncio.run(main())
