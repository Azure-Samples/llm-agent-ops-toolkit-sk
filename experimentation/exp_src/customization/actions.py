import chainlit as cl
from chainlit.data.base import BaseDataLayer
from chainlit.types import Feedback
from chainlit.logger import logger


class CustomActions:
    def __init__(self, message_id: str, thread_id: str) -> None:
        self.thumbs_up_action = cl.Action(
            label="👍",
            name="thumbs_up_action",
            tooltip="Looks Good",
            payload={"message_id": message_id, "thread_id": thread_id, "value": 1},
        )
        self.thumbs_down_action = cl.Action(
            label="👎",
            name="thumbs_down_action",
            tooltip="Needs Improvement",
            payload={"message_id": message_id, "thread_id": thread_id, "value": 0},
        )

    def get_thumbs_up_action(self) -> cl.Action:
        return self.thumbs_up_action

    def get_thumbs_down_action(self) -> cl.Action:
        return self.thumbs_down_action

    @staticmethod
    async def thumbs_up_down_action_handler(
        message_id: str,
        thread_id: str,
        value: int,
        data_layer: BaseDataLayer,
        comment: str = None,
    ) -> None:
        if data_layer:
            try:
                feedback = Feedback(
                    forId=message_id, value=value, threadId=thread_id, comment=comment
                )
                await data_layer.upsert_feedback(feedback)
            except Exception as e:
                logger.error(f"Error inserting message feedback: {e}")
