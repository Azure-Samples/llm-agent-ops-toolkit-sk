"""This module contains the AgentSelect class, which is a StateFlowBaseAgent that creates the SQL Select query to answer the question."""
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)

from .base import StateFlowBaseAgent


class AgentSelect:
    """
    Select Agent that create the SQL Select query to answer the question.
    """
    name = "select"
    # Security Guardrail 01: Explicit instruction to avoid DML, DDL, DCL, and TCL queries.
    select_agent_prompt = """Interact with a MySQL Database system using SQL queries to answer a question.

## Instructions
Based on the understanding of the tables and the problem, formulate a SQL query with SELECT that answers the question EXACTLY. Use specific clauses like WHERE, JOIN, GROUP BY, HAVING, etc if necessary.
If you need more information of another table, use DESC to explore the table.
Notes: 
- You should construct your command that the output answers the question exactly. For example, If the question asks for count, your command should output a single number. 
- Only select the field the question asks for. Do not include relevant but unnecessary fields such as ids or counts, unless the question specifically asks for it.
- No need to CAST or ROUND numbers unless the question asks for it.
- If the question will lead to write SQL Data Manipulation (DML) or Data Definition (DDL) or Data Control (DCL) or Transaction Control (TCL), please ABORT the query with this "Action: submit" command.
- Do not give any command that can manipulate the database.

## Examples:
Thought: I should write a SQL command that selects the names from a table about products in ascending order of their stocks. Stocks should not be selected.
Action: execute[SELECT name FROM products ORDER BY stocks ASC]
Thought: I can use the SUM and AVG functions to get the total number of orders and average sales values for products for Smartphones.
Action: execute[execute[SELECT SUM(order) AS total_orders, AVG(sake) AS avg_sale FROM orders WHERE products_category = 'Electronics' AND products_subcategory = 'Smartphones']
Thought: I should write a SQL query that gets the name field from customers and exclude the name of 'John Doe'.
Action: execute[SELECT name FROM customers WHERE name != 'John Doe']

## RESPONSE FORMAT
For action, put your SQL command in the execute[] block.
Reply with the following template (<...> is the field description, replace it with your own response):

Thought: <your thought on constructing command to answer the query exactly>
Action: execute[<your command>] | submit
"""

    def __init__(self, kernel: Kernel | None = None):
        """
        Initialize the Select Agent.
        
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
            instructions=self.select_agent_prompt,
            description="A Select Agent that create the SQL Select query to answer the question.",
            execution_settings=prompt_execution_settings,
        )

    def get_agent(self) -> StateFlowBaseAgent:
        """
        Return the Select Agent.
        
        Returns:
            StateFlowBaseAgent: The Select Agent.
        """
        return self.agent
