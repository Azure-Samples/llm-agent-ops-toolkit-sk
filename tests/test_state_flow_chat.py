import unittest
from unittest.mock import patch, MagicMock
from src.groupchat.state_flow_chat import get_chat_client, _create_kernel_with_chat_completion
from src.mysql.execution_env import SqlEnv
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import Agent
from semantic_kernel.kernel import Kernel
from src.groupchat.state_flow_termination_strategy import StateFlowTerminationStrategy
from src.groupchat.state_flow_selection_strategy import StateFlowSelectionStrategy

class TestStateFlowChat(unittest.TestCase):

    @patch('src.groupchat.state_flow_chat.AzureChatCompletion')
    @patch('src.groupchat.state_flow_chat.Kernel')
    def test_create_kernel_with_chat_completion(self, MockKernel, MockAzureChatCompletion):
        mock_kernel_instance = MockKernel.return_value
        mock_service_instance = MockAzureChatCompletion.return_value

        # Test without AZURE_OPENAI_CHAT_DEPLOYMENT_NAME in environment
        with patch.dict('os.environ', {}, clear=True):
            kernel = _create_kernel_with_chat_completion("test_service_id")
            self.assertEqual(MockKernel.call_count, 1)
            mock_kernel_instance.add_service.assert_called_once_with(mock_service_instance)
            self.assertEqual(kernel, mock_kernel_instance)

        # Test with AZURE_OPENAI_CHAT_DEPLOYMENT_NAME in environment
        with patch.dict('os.environ', {'AZURE_OPENAI_CHAT_DEPLOYMENT_NAME': 'test_deployment'}, clear=True):
            kernel = _create_kernel_with_chat_completion("test_service_id")
            self.assertEqual(MockKernel.call_count, 2)

    @patch('src.groupchat.state_flow_chat.AgentObserve')
    @patch('src.groupchat.state_flow_chat.AgentError')
    @patch('src.groupchat.state_flow_chat.AgentVerify')
    @patch('src.groupchat.state_flow_chat.AgentSelect')
    @patch('src.groupchat.state_flow_chat.AgentExecute')
    @patch('src.groupchat.state_flow_chat.StateFlowSelectionStrategy')
    @patch('src.groupchat.state_flow_chat.StateFlowTerminationStrategy')
    @patch('src.groupchat.state_flow_chat._create_kernel_with_chat_completion')
    def test_get_chat_client(self, mock_create_kernel, MockStateFlowTerminationStrategy, MockStateFlowSelectionStrategy, MockAgentExecute, MockAgentSelect, MockAgentVerify, MockAgentError, MockAgentObserve):
        mock_sql_env = MagicMock(spec=SqlEnv)
        mock_kernel = MagicMock(spec=Kernel)
        mock_create_kernel.return_value = mock_kernel

        mock_agent_observe = MockAgentObserve.return_value
        mock_agent_error = MockAgentError.return_value
        mock_agent_verify = MockAgentVerify.return_value
        mock_agent_select = MockAgentSelect.return_value
        mock_agent_execute = MockAgentExecute.return_value
        MockStateFlowTerminationStrategy.return_value = MagicMock(spec=StateFlowTerminationStrategy)
        MockStateFlowSelectionStrategy.return_value = MagicMock(spec=StateFlowSelectionStrategy)

        mock_agent_observe.get_agent.return_value = MagicMock(spec=Agent, name='observe_agent', id='observe')
        mock_agent_error.get_agent.return_value = MagicMock(spec=Agent, name='error_agent', id='error')
        mock_agent_verify.get_agent.return_value = MagicMock(spec=Agent, name='verify_agent', id='verify')
        mock_agent_select.get_agent.return_value = MagicMock(spec=Agent, name='select_agent', id='select')
        mock_agent_execute.get_agent.return_value = MagicMock(spec=Agent, name='execute_agent', id='execute')

        chat_client = get_chat_client(mock_sql_env)

        self.assertIsInstance(chat_client, AgentGroupChat)
        self.assertEqual(len(chat_client.agents), 5)

if __name__ == '__main__':
    unittest.main()