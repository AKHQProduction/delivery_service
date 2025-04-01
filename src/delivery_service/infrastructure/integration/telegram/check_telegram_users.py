# ruff: noqa: E501
from typing import Any
from uuid import UUID

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.bootstrap.configs import TGConfig
from delivery_service.infrastructure.persistence.adapters.social_network_gateway import (
    SQlAlchemySocialNetworkGateway,
)


class CheckTelegramUsers:
    def __init__(
        self,
        social_network_gateway: SQlAlchemySocialNetworkGateway,
        bot_config: TGConfig,
        transaction_manager: TransactionManager,
    ) -> None:
        self._dao = social_network_gateway
        self._config = bot_config
        self._transaction_manager = transaction_manager

    async def handle(self) -> None:
        total_records = await self._dao.total()
        offset = 0
        limit = 100

        while total_records > 0:
            records = await self._dao.get_telegram_data(
                offset=offset, limit=limit
            )
            offset += limit
            total_records -= limit

            data_to_update: dict[UUID, dict[str, Any]] = {}

            async with Bot(token=self._config.admin_bot_token) as bot:
                for record_id, record in records.items():
                    try:
                        account = await bot.get_chat(chat_id=record_id)
                        data_to_update[record.row_id] = {
                            "username": account.username,
                            "full_name": account.full_name,
                        }
                    except TelegramBadRequest:
                        continue

            if data_to_update:
                await self._dao.update_data(data_to_update)

        await self._transaction_manager.commit()
