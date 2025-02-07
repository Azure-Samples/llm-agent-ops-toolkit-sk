"""This module contains the StateFlowTerminationStrategy class, which is a subclass of TerminationStrategy.
It is used to determine when to terminate a conversation based on the state of the conversation flow."""
import logging
from semantic_kernel.agents.agent import Agent
from semantic_kernel.agents.strategies.termination.termination_strategy import (
    TerminationStrategy,
)
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.finish_reason import FinishReason
from src.utils.constants import Constants
from src.agents.verify import AgentVerify
from src.agents.select import AgentSelect

logger: logging.Logger = logging.getLogger(__name__)


class StateFlowTerminationStrategy(TerminationStrategy): # pylint: disable=abstract-method
    """StateFlowTerminationStrategy is a specialized termination strategy for determining when to terminate a conversation based on the state of the conversation flow."""
    maximum_iterations: int = Constants.maximum_iterations

    async def should_terminate(
        self, agent: "Agent", history: list["ChatMessageContent"]
    ) -> bool:
        """
        Determines whether the conversation should be terminated based on the current state of the conversation flow.
        
        Args:
            agent (Agent): The agent to evaluate termination for.
            history (list[ChatMessageContent]): The chat history to use for evaluation.
            
        Returns:
            bool: True if the conversation should be terminated, False otherwise.
        """
        logger.info("Evaluating termination criteria for %s", agent.id)

        # Not enough history to make a decision
        if not history:
            return False

        # Standard termination criteria
        if len(history) >= self.maximum_iterations:
            history[-1].finish_reason = FinishReason.LENGTH
            return True
        if history[-1].content == Constants.terminate_text:
            history[-1].finish_reason = FinishReason.STOP
            return True

        # State-specific termination criteria
        if len(history) >= 2:
            last_action = (
                history[-2].content.split(Constants.action_identifier)[-1].strip()
            )
            last_action = last_action.replace("\n", "")
            last_state = history[-2].name
            if last_state == AgentSelect.name:
                if Constants.action_submit in last_action:
                    history[-1].finish_reason = FinishReason.STOP
                    return True
            elif last_state == AgentVerify.name:
                if Constants.action_submit in last_action:
                    history[-1].finish_reason = FinishReason.STOP
                    return True

        # Default termination criteria
        if self.agents and not any(a.id == agent.id for a in self.agents):
            logger.info("Agent %s is out of scope", agent.id)
            return False

        # Default to not terminating
        return False
