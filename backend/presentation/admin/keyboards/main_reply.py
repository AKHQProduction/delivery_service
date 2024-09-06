from abc import ABC, abstractmethod

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from presentation.admin.consts import (
    CREATE_NEW_SHOP_TXT, GOODS_BTN_TEXT,
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
    ):
        pass

    async def render_keyboard(self) -> ReplyKeyboardMarkup:
        return UserKeyboard().render_keyboard()
