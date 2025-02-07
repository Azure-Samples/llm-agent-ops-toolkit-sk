"""This module contains the AgentError class, which is a StateFlowBaseAgent that helps to debug the SQL query and suggest the next steps.""" 
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)

from .base import StateFlowBaseAgent


class AgentError:
    """
    Error Agent that helps to debug the SQL query and suggest the next steps.
    """
    name = "error"
    error_agent_prompt = """Interact with a MySQL Database system using SQL queries to answer a question.

## Instructions
Please carefully read the error message to understand what went wrong.
If you don't have enough information to solve the question, you can use the DESC [table_name] command to explore another table.
You may want to review other tables to see if they have the information you need.

## Examples
Thought: A `transcripts` table exists, but it doesn't have the `release_date` column I came up with. I should find out what columns are available.
Thought: The `friends` table has two ids. I should check if the `highschooler` table has a name associated with an ID.
Thought: The `contestants` is a table, it is not a column in `people`. I need to check the `contestants` table to see how to get the contestant names.
Thought: I get a single number that is the number of likes that the high schooler Kyle has. This should be the answer.

## RESPONSE FORMAT
For action, put your SQL command in the execute[] block.
Reply with the following template (<...> is the field description, replace it with your own response):

Thought: <your thought on why this query is error and whether you should gather more information or fix the error in one sentence>
Action: execute[<your command>]
"""

    def __init__(self, kernel: Kernel | None = None):
        """
        Initialize the Error Agent.
        
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
            instructions=self.error_agent_prompt,
            description="An Error Agent that helps to debug the SQL query and suggest the next steps.",
            execution_settings=prompt_execution_settings,
        )

    def get_agent(self) -> StateFlowBaseAgent:
        """
        Return the Error Agent.
        
        Returns:
            StateFlowBaseAgent: The Error Agent.
        """
        return self.agent
