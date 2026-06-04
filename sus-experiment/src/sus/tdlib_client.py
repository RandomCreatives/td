import asyncio
from aiotdlib import Client, ClientSettings
from aiotdlib.api import API, UpdateNewMessage, MessageText
from sus.config import settings
import structlog

logger = structlog.get_logger()

class TDLibClient:
    def __init__(self):
        self.client = Client(
            settings=ClientSettings(
                api_id=settings.api_id,
                api_hash=settings.api_hash,
                phone_number=settings.phone_number,
                use_message_database=False,
                use_chat_info_database=False,
                use_file_database=False,
            )
        )
        self.message_handlers = []

    def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    async def start(self):
        @self.client.on_event(UpdateNewMessage)
        async def on_new_message(event: UpdateNewMessage):
            for handler in self.message_handlers:
                await handler(event.message)

        await self.client.start()
        logger.info("TDLib client started")

    async def send_text(self, chat_id: int, text: str):
        await self.client.api.send_message(
            chat_id=chat_id,
            input_message_content=MessageText(text=text)
        )

    async def delete_messages(self, chat_id: int, message_ids: list[int]):
        await self.client.api.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True
        )

td_client = TDLibClient()
