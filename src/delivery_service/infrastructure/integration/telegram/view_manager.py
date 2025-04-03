# ruff: noqa: E501
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.bootstrap.configs import TGConfig
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_role import Role
from delivery_service.infrastructure.integration.telegram.const import (
    CREATE_SHOP_BTN,
)
from delivery_service.infrastructure.persistence.adapters.social_network_gateway import (
    SQlAlchemySocialNetworkGateway,
)


class TelegramViewManager(ViewManager):
    def __init__(
        self,
        idp: IdentityProvider,
        tg_config: TGConfig,
        dao: SQlAlchemySocialNetworkGateway,
    ) -> None:
        self._idp = idp
        self._config = tg_config
        self._dao = dao

    async def _send_message(
        self,
        telegram_id: int,
        text: str,
        reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None,
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

        current_roles = await self._idp.get_current_staff_roles()

        if any(role.name == Role.USER for role in current_roles):
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=CREATE_SHOP_BTN)]],
                resize_keyboard=True,
            )

            await self._send_message(
                telegram_id=telegram_id,
                text="Hello, user",
                reply_markup=reply_markup,
            )
