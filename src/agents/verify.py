"""This module contains the Verify Agent class that helps to verify the SQL query output if it answers the question or suggests the next steps."""
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)

from .base import StateFlowBaseAgent


class AgentVerify:
    """
    Verify Agent that helps to verify the SQL query output if it answers the question or suggests the next steps.
    """
    name = "verify"
    # Security Guardrail 01: Explicit instruction to avoid DML, DDL, DCL, and TCL queries.
    verify_agent_prompt = """Interact with a MySQL Database system using SQL queries to answer a question.

## Instructions
Carefully check if the output answers the question exactly.
Make sure the output only display fields that the problem asks for. 
- If the output contains any extra fields, please revise and modify your query (column alias is fine, no need to round numbers).
- If the output doesn't answer the question, please revise and modify your query. You may use DESC/DESCRIBE to learn more about the tables.
- If the output answers the question exactly, please submit the query with this "Action: submit" command.
- If the question will lead to write SQL Data Manipulation (DML) or Data Definition (DDL) or Data Control (DCL) or Transaction Control (TCL), please ABORT the query with this "Action: submit" command.
- Do not give any command that can manipulate the database.

## Examples
Thought: The output displays the contestant names and also contestant count. Although the count is used for sorting, it should not be displayed in output. I should modify my query to only select the contestant names.
Thought: The question asks for the total population for North America. However, the output also has the continent id. I should modify my query to only select the total population.

## RESPONSE FORMAT
For action, put your SQL command in the execute[] block. If the problem is solved, your action should be "Action: submit".
Reply with the following template (<...> is the field description, replace it with your own response, "|" is the "or" operation):

Thought: <your thought on whether the output and command answers the problem>
Action: execute[<your new command>] | submit
"""

    def __init__(self, kernel: Kernel | None = None):
        """
        Initialize the Verify Agent.
        
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
            instructions=self.verify_agent_prompt,
            description="A Verify Agent that helps to verify the SQL query output if it answers the question or suggests the next steps.",
            execution_settings=prompt_execution_settings,
        )

    def get_agent(self) -> StateFlowBaseAgent:
        """
        Return the Verify Agent.
        
        Returns:
            StateFlowBaseAgent: The Verify Agent.
        """
        return self.agent
