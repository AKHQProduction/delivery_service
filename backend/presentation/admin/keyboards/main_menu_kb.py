from abc import ABC, abstractmethod

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from entities.employee.models import EmployeeRole
from presentation.admin.consts import (
    CREATE_NEW_SHOP_BTN_TXT,
    FAQ_BTN_TXT,
    GOODS_BTN_TEXT,
    STAFF_BTN_TXT,
)


class KeyboardByRole(ABC):
    @abstractmethod
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        raise NotImplementedError


class AdminKeyboard(KeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=STAFF_BTN_TXT)],
                [KeyboardButton(text=GOODS_BTN_TEXT)],
            ],
            resize_keyboard=True,
        )


class UserKeyboard(KeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=CREATE_NEW_SHOP_BTN_TXT)],
                [KeyboardButton(text=FAQ_BTN_TXT)],
            ],
            resize_keyboard=True,
        )


class MainReplyKeyboard:
    def __init__(self, role: EmployeeRole | None):
        self.role = role

    async def render_keyboard(self) -> ReplyKeyboardMarkup | None:
        if not self.role:
            return UserKeyboard().render_keyboard()
        if self.role == EmployeeRole.ADMIN:
            return AdminKeyboard().render_keyboard()
        return None
