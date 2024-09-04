from abc import ABC, abstractmethod

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from entities.user.models.user import RoleName
from presentation.admin.consts import (
    CREATE_NEW_SHOP_TXT, CREATE_ORDER_BTN_TXT,
    GOODS_BTN_TEXT,
    MY_ORDERS_BTN_TXT,
    PROFILE_BTN_TXT,
    STAFF_BTN_TXT
)


class IKeyboardByRole(ABC):
    @abstractmethod
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        raise NotImplementedError


class AdminKeyboard(IKeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text=STAFF_BTN_TXT)
                    ],
                    [
                        KeyboardButton(text=GOODS_BTN_TEXT)
                    ]
                ],
                resize_keyboard=True
        )


class UserKeyboard(IKeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text=CREATE_NEW_SHOP_TXT)
                    ],
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
