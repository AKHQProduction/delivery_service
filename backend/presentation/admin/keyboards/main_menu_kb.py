from abc import ABC, abstractmethod

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from entities.employee.models import EmployeeRole
from presentation.common.consts import (
    CREATE_SHOP_BTN_TXT,
    EMPLOYEE_BTN_TXT,
    FAQ_BTN_TXT,
    GOODS_BTN_TEXT,
    PROFILE_BTN_TXT,
)

faq_btn = KeyboardButton(text=FAQ_BTN_TXT)
profile_btn = KeyboardButton(text=PROFILE_BTN_TXT)


class KeyboardByRole(ABC):
    @abstractmethod
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        raise NotImplementedError


class AdminKeyboard(KeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [profile_btn],
                [
                    KeyboardButton(text=EMPLOYEE_BTN_TXT),
                    KeyboardButton(text=GOODS_BTN_TEXT),
                ],
                [faq_btn],
            ],
            resize_keyboard=True,
        )


class UserKeyboard(KeyboardByRole):
    def render_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [profile_btn],
                [KeyboardButton(text=CREATE_SHOP_BTN_TXT)],
                [faq_btn],
            ],
            resize_keyboard=True,
        )


keyboards = {EmployeeRole.ADMIN: AdminKeyboard, "DEFAULT": UserKeyboard}


class MainReplyKeyboard:
    def __init__(self, role: EmployeeRole | None):
        self.role = role

    async def render_keyboard(self) -> ReplyKeyboardMarkup | None:
        if not self.role:
            return UserKeyboard().render_keyboard()
        return keyboards[self.role]().render_keyboard()
