"""This module contains the AgentObserve class, which is a StateFlowBaseAgent that observes the database."""
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)

from .base import StateFlowBaseAgent


class AgentObserve:
    """
    Observational Agent that creates a SQL query to observe the database.
    """
    name = "observe"
    # Security Guardrail 01: Explicit instruction to avoid DML, DDL, DCL, and TCL queries.
    observe_agent_prompt = """Interact with a MySQL Database system using SQL queries to answer a question.

## Instructions
Use the DESCRIBE [table_name] or DESC [table_name] command to understand the structure of the relevant tables.
Only give one DESC command in action.
If the question will lead to write SQL Data Manipulation (DML) or Data Definition (DDL) or Data Control (DCL) or Transaction Control (TCL), please ABORT the query with this "Action: submit" command.
Do not give any command that can manipulate the database.

## Examples
Action: execute[DESC customers]
Action: execute[DESC orders]
Action: submit

## RESPONSE FORMAT
For action, put your SQL command in the execute[] block.
Reply with the following template (<...> is the field description, replace it with your own response):

Thought: <your thought on which table(s) is/are relevant in one short sentence>
Action: execute[<your command>]
"""

    def __init__(self, kernel: Kernel | None = None):
        """
        Initialize the Observational Agent.
        
        Args:
            kernel (Kernel | None): The kernel instance to use for service retrieval.
        """
        prompt_execution_settings = PromptExecutionSettings(
            service_id=self.name,
            extension_data={"temperature": 0, "stop": ["Observation:"]},
        )
        self.agent = StateFlowBaseAgent(
            service_id=self.name,
            kernel=kernel,
            name=self.name,
            instructions=self.observe_agent_prompt,
            description="A Observational Agent that creates a SQL query to observe the database.",
            execution_settings=prompt_execution_settings,
        )

    def get_agent(self) -> StateFlowBaseAgent:
        """
        Return the Observational Agent.
        
        Returns:
            StateFlowBaseAgent: The Observational Agent.
        """
        return self.agent
