from aiogram import Bot

from delivery_service.application.common.dto import TelegramContactsData
from delivery_service.application.ports.social_network_checker import (
    SocialNetworkChecker,
)
from delivery_service.domain.shared.dto import Empty


class SocialNetworkCheckerImpl(SocialNetworkChecker):
    def __init__(self, bot: Bot | None) -> None:
        self._telegram_bot = bot

    async def check_telegram_data(
        self, telegram_id: int
    ) -> TelegramContactsData | None:
        if not self._telegram_bot:
            return None

        chat = await self._telegram_bot.get_chat(telegram_id)
        username = chat.username if chat.username else Empty.UNSET

        return TelegramContactsData(
            telegram_id=telegram_id,
            full_name=chat.full_name,
            telegram_username=username,
        )
