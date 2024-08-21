from abc import ABC, abstractmethod

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from application.common.identity_provider import IdentityProvider
from domain.entities.user import RoleName


class IKeyboardByRole(ABC):
    @abstractmethod
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        raise NotImplementedError


class AdminKeyboard(IKeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="👥 Персонал")
                    ]
                ],
                resize_keyboard=True
        )


class UserKeyboard(IKeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="🛒 Створити замовлення")
                    ],
                    [
                        KeyboardButton(text="🗄 Мої замовлення")
                    ]
                ],
                resize_keyboard=True
        )


class MainReplyKeyboard:
    def __init__(
            self,
            role: RoleName,
    ):
        self._role = role
        self._keyboards = {
            RoleName.USER: UserKeyboard(),
            RoleName.ADMIN: AdminKeyboard()
        }

    async def render_keyboard(self) -> ReplyKeyboardMarkup:
        keyboard: IKeyboardByRole = self._keyboards.get(self._role)

        return keyboard.render_keyboard()
