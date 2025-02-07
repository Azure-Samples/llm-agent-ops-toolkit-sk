"""Base agent for chat completion within a state flow context."""
import logging
from collections.abc import AsyncIterable
from semantic_kernel.kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.connectors.ai.prompt_execution_settings import (
    PromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.exceptions import KernelServiceNotFoundError

logger: logging.Logger = logging.getLogger(__name__)


class StateFlowBaseAgent(ChatCompletionAgent):
    """
    StateFlowBaseAgent is a specialized agent for handling chat completions
    within a state flow context. It extends the ChatCompletionAgent and 
    provides additional functionality for invoking chat completion services 
    and managing chat history.
    """
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
        Initializes the StateFlowBaseAgent with the given parameters.
        
        Args:
            service_id (str | None): The ID of the chat completion service.
            kernel (Kernel | None): The kernel instance to use for service retrieval.
            name (str | None): The name of the agent.
            id (str | None): The ID of the agent.
            description (str | None): A description of the agent.
            instructions (str | None): Instructions for the agent.
            execution_settings (PromptExecutionSettings | None): Settings for prompt execution.
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

    async def invoke(self, history: ChatHistory) -> AsyncIterable[ChatMessageContent]:
        """
        Asynchronously invokes the chat completion service with the provided chat history.
        
        Args:
            history (ChatHistory): The chat history to use for the invocation.
            
        Raises:
            KernelServiceNotFoundError: If the chat completion service is not found.
            
        Yields:
            AsyncIterable[ChatMessageContent]: The chat message contents as they are generated.
        """
        # Get the chat completion service
        chat_completion_service = self.kernel.get_service(
            service_id=self.service_id, type=ChatCompletionClientBase
        )

        if not chat_completion_service:
            raise KernelServiceNotFoundError(
                f"Chat completion service not found with service_id: {self.service_id}"
            )

        assert isinstance(chat_completion_service, ChatCompletionClientBase)  # nosec

        settings = (
            self.execution_settings
            or self.kernel.get_prompt_execution_settings_from_service_id(
                self.service_id
            )
            or chat_completion_service.instantiate_prompt_execution_settings(
                service_id=self.service_id,
                extension_data={"ai_model_id": chat_completion_service.ai_model_id},
            )
        )

        chat = self._setup_agent_chat_history(history)

        message_count = len(chat)

        logger.debug(
            "[%s] Invoking %s.",
            type(self).__name__,
            type(chat_completion_service).__name__,
        )

        messages = await chat_completion_service.get_chat_message_contents(
            chat_history=chat,
            settings=settings,
            kernel=self.kernel,
        )

        logger.info(
            "[%s] Invoked %s with message count: %d.",
            type(self).__name__,
            type(chat_completion_service).__name__,
            message_count
        )

        # Verify if thought and action are generated
        result = messages[-1]
        thought_action = result.content.strip()
        try:
            a = thought_action.strip().split("Action: ")
            thought, action = a[0], a[1]
        except IndexError:
            # Fail to split, assume last step is thought, call model again to get action assume last step is thought
            thought = thought_action.strip()
            if not "Thought:" in thought:
                thought = f"Thought: {thought}"
            chat[-1].content += f"\n{thought}\nAction: "
            messages = await chat_completion_service.get_chat_message_contents(
                chat_history=chat,
                settings=settings,
                kernel=self.kernel,
            )
            action = result.content.strip()
        thought_action = f"{thought.strip()}\nAction: {action.strip()}"

        # Capture mutated messages related function calling / tools
        for message_index in range(message_count, len(chat)):
            message = chat[message_index]
            message.name = self.name
            history.add_message(message)

        for message in messages:
            message.name = self.name
            message.content = thought_action
            yield message
