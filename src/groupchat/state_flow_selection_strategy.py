"""This module contains the StateFlowSelectionStrategy class, 
which is responsible for selecting the next agent based on the current state of the conversation flow."""
import logging
from semantic_kernel.agents.strategies.selection.selection_strategy import (
    SelectionStrategy,
)
from semantic_kernel.agents import Agent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from src.agents.observe import AgentObserve
from src.agents.select import AgentSelect
from src.agents.verify import AgentVerify
from src.agents.error import AgentError
from src.agents.execute import AgentExecute
from src.utils.constants import Constants

logger: logging.Logger = logging.getLogger(__name__)


class StateFlowSelectionStrategy(SelectionStrategy):
    """StateFlowSelectionStrategy is a specialized selection strategy for selecting the next agent based on the current state of the conversation flow."""
    async def next(
        self, agents: list[Agent], history: list[ChatMessageContent]
    ) -> Agent:
        """
        Selects the next agent based on the current state of the conversation flow.
        
        Args:
            agents (list[Agent]): The list of agents to select from.
            history (list[ChatMessageContent]): The chat history to use for selection.
        
        Raises:
            ValueError: If an unknown state is encountered in the conversation flow.
        
        Returns:
            Agent: The next agent to invoke.
        """
        last_message = history[-1].content
        last_speaker = history[-1].name

        # From user it will always go to observe
        if history[-1].role.value == AuthorRole.USER:
            return [agent for agent in agents if agent.name == AgentObserve.name][0]
        # It's always M->E aka Model->Execute, means after each LLM Agent it will go to Execute
        if last_speaker != AgentExecute.name:
            return [agent for agent in agents if agent.name == AgentExecute.name][0]
        # If the last message is None or contains the SQL error message, it will go to the Error Agent
        if last_message is None or Constants.sql_error_message in last_message:
            return [agent for agent in agents if agent.name == AgentError.name][0]

        # Retrieve the last action and state
        last_action = history[-2].content.split(Constants.action_identifier)[-1].strip()
        last_action = last_action.replace("\n", "")
        last_state = history[-2].name

        # State-specific selection criteria
        # If the last state is Observe, it will go to Select, if no error
        if last_state == AgentObserve.name: # pylint: disable=no-else-return
            return [agent for agent in agents if agent.name == AgentSelect.name][0]
        # If the last state is Select, it will go to Verify if the last SQL Query is SELECT, else it will go back to Select
        elif last_state == AgentSelect.name:
            if Constants.execute_select in last_action:
                return [agent for agent in agents if agent.name == AgentVerify.name][0]
            return [agent for agent in agents if agent.name == AgentSelect.name][0]
        # If the last state is Verify, it will go to Verify if the last SQL Query is SELECT, else it will go back to Select
        elif last_state == AgentVerify.name:
            if Constants.execute_select in last_action:
                return [agent for agent in agents if agent.name == AgentVerify.name][0]
            return [agent for agent in agents if agent.name == AgentSelect.name][0]
        # If the last state is Error, it will go to Verify if the last SQL Query is SELECT, else it will go back to Select
        elif last_state == AgentError.name:
            if Constants.execute_select in last_action:
                return [agent for agent in agents if agent.name == AgentVerify.name][0]
            return [agent for agent in agents if agent.name == AgentSelect.name][0]
        else:
            raise ValueError(f"Unknown state in state flow: {last_state}")
