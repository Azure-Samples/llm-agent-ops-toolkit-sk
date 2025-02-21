"""This module contains the AgentExecute class that is responsible for executing the SQL code and returning the output."""
import re
import logging
from typing import Optional
from collections.abc import AsyncIterable
from semantic_kernel.kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.text_content import TextContent

from src.mysql.execution_env import SqlEnv
from src.utils.constants import Constants

logger: logging.Logger = logging.getLogger(__name__)


class SQLExecuteAgent(ChatCompletionAgent):
    """
    Agent base implementation for executing SQL code and returning the output.
    """
    env: Optional[SqlEnv] = None

    def __init__(
        self,
        service_id: str | None = None,
        kernel: Kernel | None = None,
        name: str | None = None,
        id: str | None = None,
        description: str | None = None,
        instructions: str | None = None,
        execution_settings: PromptExecutionSettings | None = None,
    ):
        """
        Initialize the SQLExecuteAgent.
        
        Args:
            service_id (str | None): The service id of the agent.
            kernel (Kernel | None): The kernel instance.
            name (str | None): The name of the agent.
            id (str | None): The id of the agent.
            description (str | None): The description of the agent.
            instructions (str | None): The instructions for the agent.
            execution_settings (PromptExecutionSettings | None): The execution settings for the agent.
        """
        super().__init__(
            service_id=service_id,
            kernel=kernel,
            name=name,
            id=id,
            description=description,
            instructions=instructions,
            execution_settings=execution_settings,
        )

    def sql_parser_react(self, action: str) -> tuple[str, bool]:
        """
        Parse the SQL code from the action.
        
        Args:
            action (str): The action to parse.
            
        Returns:
            tuple[str, bool]: The parsed action and a boolean indicating if the action is valid.
        """
        if action == Constants.action_submit:
            return action, True
        pattern = r"execute\[(.*)\]"
        matches = re.findall(pattern, action, re.DOTALL)
        if len(matches) > 0:
            action = matches[0]
            if ";" in action:
                return action[: action.index(";")], True
            return action, True
        return action, False

    async def invoke(self, history: ChatHistory) -> AsyncIterable[ChatMessageContent]:
        """
        Execute the SQL code and return the output.
        
        Args:
            history (ChatHistory): The chat history.
        
        Yields:
            AsyncIterable[ChatMessageContent]: The output message.
        """
        chat = self._setup_agent_chat_history(history)
        message = chat[-1].content

        logger.info(
            "[%s] Invoked %s with message count: %d.",
            type(self).__name__,
            "code_executor",
            len(chat),
        )

        a = message.strip().split(f"{Constants.action_identifier} ")
        try:
            _, action = a[0], a[1]
            action_parsed, is_code = self.sql_parser_react(action)
        except IndexError:
            action_parsed, is_code = None, False
        if not is_code:
            observation = f"{Constants.sql_error_message}: Your last `execute` action did not contain SQL code"
            if Constants.sql_show_database in action_parsed:
                observation = f"{Constants.sql_error_message}: SHOW DATABASES is not allowed in this environment."
        else:
            # Security Guardrail 02: Check for SQL Data Manipulation related keywords
            if any(
                keyword.lower() + " " in action_parsed.lower()
                for keyword in Constants.sql_data_manipulation_commands
            ):
                observation = f"{Constants.sql_error_message}: SQL Data Manipulation Language (DML) is not allowed in this environment."
            else:
                observation, _, _, _ = self.env.step(action_parsed)

        # Limit observation size due to context window thresholds for API call
        if isinstance(observation, str) and len(observation) > 350:
            observation = observation[:350]
        elif isinstance(observation, list) and len(observation) > 25:
            observation = observation[:25]

        code_output = f"{Constants.observation_identifier}{observation}"

        output_message = ChatMessageContent(
            role=AuthorRole.ASSISTANT,
            items=[TextContent(text=code_output)],
            name=self.name,
        )
        messages = [output_message]
        history.add_message(output_message)
        for message in messages:
            yield message


class AgentExecute:
    """
    Agent that executes the SQL code and returns the output.
    """
    name = "executor"

    def __init__(self, sql_executor_env: SqlEnv, kernel: Kernel | None = None):
        """
        Initialize the AgentExecute.
        
        Args:
            sql_executor_env (SqlEnv): The SQL execution environment.
            kernel (Kernel | None): The kernel instance.
        """
        self.agent = SQLExecuteAgent(
            name=self.name,
            service_id=self.name,
            kernel=kernel,
            description="A Code Executor Agent that executes the SQL query and returns the output.",
        )
        self.agent.env = sql_executor_env

    def get_agent(self) -> SQLExecuteAgent:
        """
        Get the AgentExecute instance.
        
        Returns:
            SQLExecuteAgent: The AgentExecute instance.
        """
        return self.agent
