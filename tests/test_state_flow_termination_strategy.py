import unittest
from unittest.mock import AsyncMock, MagicMock
from src.groupchat.state_flow_termination_strategy import StateFlowTerminationStrategy
from semantic_kernel.agents.agent import Agent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.finish_reason import FinishReason
from src.utils.constants import Constants
from src.agents.verify import AgentVerify
from src.agents.select import AgentSelect

class TestStateFlowTerminationStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = StateFlowTerminationStrategy()
        self.agent = MagicMock(spec=Agent)
        self.agent.id = "test_agent"

    async def test_should_terminate_no_history(self):
        history = []
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertFalse(result)

    async def test_should_terminate_maximum_iterations(self):
        history = [MagicMock(spec=ChatMessageContent) for _ in range(Constants.maximum_iterations)]
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertTrue(result)
        self.assertEqual(history[-1].finish_reason, FinishReason.LENGTH)

    async def test_should_terminate_terminate_text(self):
        history = [MagicMock(spec=ChatMessageContent) for _ in range(2)]
        history[-1].content = Constants.terminate_text
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertTrue(result)
        self.assertEqual(history[-1].finish_reason, FinishReason.STOP)

    async def test_should_terminate_agent_select_action_submit(self):
        history = [MagicMock(spec=ChatMessageContent) for _ in range(2)]
        history[-2].content = f"Some content {Constants.action_identifier} {Constants.action_submit}"
        history[-2].name = AgentSelect.name
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertTrue(result)
        self.assertEqual(history[-1].finish_reason, FinishReason.STOP)

    async def test_should_terminate_agent_verify_action_submit(self):
        history = [MagicMock(spec=ChatMessageContent) for _ in range(2)]
        history[-2].content = f"Some content {Constants.action_identifier} {Constants.action_submit}"
        history[-2].name = AgentVerify.name
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertTrue(result)
        self.assertEqual(history[-1].finish_reason, FinishReason.STOP)

    async def test_should_not_terminate_agent_out_of_scope(self):
        self.strategy.agents = [MagicMock(spec=Agent)]
        self.strategy.agents[0].id = "other_agent"
        history = [MagicMock(spec=ChatMessageContent) for _ in range(1)]
        result = await self.strategy.should_terminate(self.agent, history)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()