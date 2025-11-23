import uuid

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link

from backend.application.usecases.invite_employee.interfaces import (
    GeneratedLink,
    InviteLinkGenerator,
)
from backend.bootstrap.config import TelegramConfig


class TelegramInviteLinkGenerator(InviteLinkGenerator):
    def __init__(self, config: TelegramConfig) -> None:
        self._config = config

    async def generate(self) -> GeneratedLink:
        payload = f"invite_link_{uuid.uuid4()}"

        async with Bot(token=self._config.admin_token) as bot:
            link = await create_start_link(bot, payload, True)

        return GeneratedLink(link=link, payload=payload)
