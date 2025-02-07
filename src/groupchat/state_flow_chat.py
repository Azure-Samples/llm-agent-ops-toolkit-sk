"""This module contains the implementation of the chat client for the group chat state flow."""
import os
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from src.mysql.execution_env import SqlEnv
from src.agents.observe import AgentObserve
from src.agents.error import AgentError
from src.agents.verify import AgentVerify
from src.agents.select import AgentSelect
from src.agents.execute import AgentExecute
from src.groupchat.state_flow_termination_strategy import StateFlowTerminationStrategy
from src.groupchat.state_flow_selection_strategy import StateFlowSelectionStrategy


def _create_kernel_with_chat_completion(service_id: str) -> Kernel:
    """
    Creates a kernel with a chat completion service.
    
    Args:
        service_id (str): The ID of the chat completion service.
    
    Returns:
        Kernel: The kernel with the chat completion service.
    """
    kernel = Kernel()
    if "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME" not in os.environ:
        kernel.add_service(AzureChatCompletion(service_id=service_id))
    else:
        kernel.add_service(
            AzureChatCompletion(
                service_id=service_id,
                deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
            )
        )
    return kernel


def get_chat_client(sql_executor_env: SqlEnv) -> AgentGroupChat:
    """
    Gets the chat client for the group chat state flow.
    
    Args:
        sql_executor_env (SqlEnv): The SQL execution environment.
        
    Returns:
        AgentGroupChat: The chat client for the group chat state flow.
    """
    agent_observe = AgentObserve(
        kernel=_create_kernel_with_chat_completion("observe")
    ).get_agent()
    agent_error = AgentError(
        kernel=_create_kernel_with_chat_completion("error")
    ).get_agent()
    agent_verify = AgentVerify(
        kernel=_create_kernel_with_chat_completion("verify")
    ).get_agent()
    agent_select = AgentSelect(
        kernel=_create_kernel_with_chat_completion("select")
    ).get_agent()
    agent_execute = AgentExecute(
        sql_executor_env=sql_executor_env,
        kernel=_create_kernel_with_chat_completion("execute"),
    ).get_agent()

    selection_strategy = StateFlowSelectionStrategy()
    termination_strategy = StateFlowTerminationStrategy()

    chat = AgentGroupChat(
        agents=[agent_observe, agent_error, agent_verify, agent_select, agent_execute],
        termination_strategy=termination_strategy,
        selection_strategy=selection_strategy,
    )
    return chat
