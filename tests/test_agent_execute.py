import unittest
from unittest.mock import AsyncMock, MagicMock
from src.agents.execute import SQLExecuteAgent, AgentExecute
from src.mysql.execution_env import SqlEnv
from semantic_kernel.kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from src.utils.constants import Constants

class TestSQLExecuteAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sql_env = MagicMock(spec=SqlEnv)
        self.kernel = MagicMock(spec=Kernel)
        self.agent_execute = AgentExecute(sql_executor_env=self.sql_env, kernel=self.kernel)
        self.agent = self.agent_execute.get_agent()

    def test_sql_parser_react_valid_action(self):
        action = "execute[SELECT * FROM users;]"
        parsed_action, is_valid = self.agent.sql_parser_react(action)
        self.assertEqual(parsed_action, "SELECT * FROM users")
        self.assertTrue(is_valid)

    def test_sql_parser_react_invalid_action(self):
        action = "invalid_action"
        parsed_action, is_valid = self.agent.sql_parser_react(action)
        self.assertEqual(parsed_action, "invalid_action")
        self.assertFalse(is_valid)

    def test_sql_parser_react_submit_action(self):
        action = Constants.action_submit
        parsed_action, is_valid = self.agent.sql_parser_react(action)
        self.assertEqual(parsed_action, Constants.action_submit)
        self.assertTrue(is_valid)

    async def test_invoke_valid_sql(self):
        history = ChatHistory()
        history.add_message(ChatMessageContent(role=AuthorRole.USER, items=[], content=f"{Constants.action_identifier} execute[SELECT * FROM users;]"))
        self.sql_env.step.return_value=("result", None, None, None)

        messages = [message async for message in self.agent.invoke(history)]
        self.assertEqual(len(messages), 1)
        self.assertIn("result", messages[0].items[0].text)

    async def test_invoke_invalid_sql(self):
        history = ChatHistory()
        history.add_message(ChatMessageContent(role=AuthorRole.USER, items=[], content=f"{Constants.action_identifier} invalid_action"))

        messages = [message async for message in self.agent.invoke(history)]
        self.assertEqual(len(messages), 1)
        self.assertIn(Constants.sql_error_message, messages[0].items[0].text)

    async def test_invoke_show_databases(self):
        history = ChatHistory()
        history.add_message(ChatMessageContent(role=AuthorRole.USER, items=[], content=f"{Constants.action_identifier} execute SHOW DATABASES"))
        self.sql_env.step.return_value=("result", None, None, None)

        messages = [message async for message in self.agent.invoke(history)]
        self.assertEqual(len(messages), 1)
        self.assertIn("SHOW DATABASES is not allowed", messages[0].items[0].text)

if __name__ == "__main__":
    unittest.main()