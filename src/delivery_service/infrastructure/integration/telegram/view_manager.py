# ruff: noqa: E501

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.bootstrap.configs import TGConfig
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.integration.telegram.kbd import (
    get_shop_staff_main_kbd,
)
from delivery_service.infrastructure.persistence.adapters.social_network_dao import (
    SQlAlchemySocialNetworkGateway,
)


class TelegramViewManager(ViewManager):
    def __init__(
        self,
        tg_config: TGConfig,
        dao: SQlAlchemySocialNetworkGateway,
        idp: IdentityProvider,
    ) -> None:
        self._config = tg_config
        self._dao = dao
        self._idp = idp

    async def _send_message(
        self,
        telegram_id: int,
        text: str,
        reply_markup: ReplyKeyboardMarkup
        | InlineKeyboardMarkup
        | None
        | ReplyKeyboardRemove,
    ) -> None:
        async with Bot(token=self._config.admin_bot_token) as bot:
            await bot.send_message(
                chat_id=telegram_id, text=text, reply_markup=reply_markup
            )

    async def _get_telegram_id(self, user_id: UserID) -> int | None:
        return await self._dao.get_current_user_telegram_id(user_id)

    async def send_greeting_message(self, user_id: UserID) -> None:
        telegram_id = await self._get_telegram_id(user_id=user_id)
        if not telegram_id:
            raise ValueError()

        if current_user_roles := await self._idp.get_current_staff_roles():
            roles = [role.name for role in current_user_roles]
        else:
            roles = []

        await self._send_message(
            telegram_id=telegram_id,
            text="Hello, user",
            reply_markup=get_shop_staff_main_kbd(roles),
        )
