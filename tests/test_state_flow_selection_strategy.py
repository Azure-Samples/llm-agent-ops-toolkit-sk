import unittest
from unittest.mock import AsyncMock, MagicMock
from src.groupchat.state_flow_selection_strategy import StateFlowSelectionStrategy
from semantic_kernel.agents import Agent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from src.agents.observe import AgentObserve
from src.agents.select import AgentSelect
from src.agents.verify import AgentVerify
from src.agents.error import AgentError
from src.agents.execute import AgentExecute
from src.utils.constants import Constants

class TestStateFlowSelectionStrategy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.strategy = StateFlowSelectionStrategy()
        self.agents = [
            AgentObserve().get_agent(),
            AgentSelect().get_agent(),
            AgentVerify().get_agent(),
            AgentError().get_agent(),
            AgentExecute(None).get_agent()
        ]
        self.history = []

    async def test_next_observe(self):
        self.history = [
            ChatMessageContent(content="Hello", name="user", role=AuthorRole.USER)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentObserve.name)

    async def test_next_execute(self):
        self.history = [
            ChatMessageContent(content="Hello", name="User", role=AuthorRole.USER),
            ChatMessageContent(content="Some text", name=AgentObserve.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentExecute.name)

    async def test_next_error(self):
        self.history = [
            ChatMessageContent(content=Constants.sql_error_message, name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentError.name)

    async def test_next_select(self):
        self.history = [
            ChatMessageContent(content="Some text", name=AgentObserve.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentSelect.name)
    
    async def test_next_verify_where_last_state_is_select(self):
        self.history = [
            ChatMessageContent(content=f"Some text: {Constants.execute_select}", name=AgentSelect.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentVerify.name)
    
    async def test_next_select_where_last_state_is_select(self):
        self.history = [
            ChatMessageContent(content="Some text", name=AgentSelect.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentSelect.name)
    
    async def test_next_verify_where_last_state_is_verify(self):
        self.history = [
            ChatMessageContent(content=f"Some text: {Constants.execute_select}", name=AgentVerify.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentVerify.name)
    
    async def test_next_select_where_last_state_is_verify(self):
        self.history = [
            ChatMessageContent(content="Some text", name=AgentVerify.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentSelect.name)
    
    async def test_next_verify_where_last_state_is_error(self):
        self.history = [
            ChatMessageContent(content=f"Some text: {Constants.execute_select}", name=AgentError.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentVerify.name)
    
    async def test_next_select_where_last_state_is_error(self):
        self.history = [
            ChatMessageContent(content="Some text", name=AgentError.name, role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        next_agent = await self.strategy.next(self.agents, self.history)
        self.assertEqual(next_agent.name, AgentSelect.name)

    async def test_next_unknown_state(self):
        self.history = [
            ChatMessageContent(content="Some text", name="UNKNOWN", role=AuthorRole.ASSISTANT),
            ChatMessageContent(content="SQL Result", name=AgentExecute.name, role=AuthorRole.ASSISTANT)
        ]
        with self.assertRaises(ValueError):
            await self.strategy.next(self.agents, self.history)

if __name__ == "__main__":
    unittest.main()