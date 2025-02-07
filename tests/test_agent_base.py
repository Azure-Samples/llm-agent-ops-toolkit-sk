import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.exceptions import KernelServiceNotFoundError
from src.agents.base import StateFlowBaseAgent

class TestStateFlowBaseAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.kernel = MagicMock(spec=Kernel)
        self.chat_completion_service = MagicMock(spec=ChatCompletionClientBase)
        self.kernel.get_service.return_value = self.chat_completion_service
        self.execution_settings = MagicMock(spec=PromptExecutionSettings)
        self.agent = StateFlowBaseAgent(
            service_id="test_service",
            kernel=self.kernel,
            name="test_agent",
            id="test_id",
            description="test_description",
            instructions="test_instructions",
            execution_settings=self.execution_settings,
        )
        self.chat_history = MagicMock(spec=ChatHistory)

    @patch('src.agents.base.logger')
    async def test_invoke_success(self, mock_logger):
        self.chat_completion_service.get_chat_message_contents = AsyncMock(
            return_value=[ChatMessageContent(content="Thought: test_thought\nAction: test_action", role="assistant", name="test_agent")]
        )
        self.agent._setup_agent_chat_history = MagicMock(return_value=self.chat_history)
        self.chat_history.__len__.return_value = 1

        result = [message async for message in self.agent.invoke(self.chat_history)]

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].content, "Thought: test_thought\nAction: test_action")
        self.assertEqual(result[0].name, "test_agent")

    @patch('src.agents.base.logger')
    async def test_invoke_thought_only(self, mock_logger):
        self.chat_completion_service.get_chat_message_contents = AsyncMock(
            return_value=[ChatMessageContent(content="test_thought", role="assistant", name="test_agent")]
        )
        self.agent._setup_agent_chat_history = MagicMock(return_value=self.chat_history)
        self.chat_history.__len__.return_value = 1

        result = [message async for message in self.agent.invoke(self.chat_history)]

        self.assertEqual(len(result), 1)
        self.assertIn("Thought: test_thought", result[0].content)
        self.assertIn("Action: ", result[0].content)
        self.assertEqual(result[0].name, "test_agent")

if __name__ == '__main__':
    unittest.main()