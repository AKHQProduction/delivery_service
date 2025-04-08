from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from delivery_service.domain.staff.staff_role import Role
from delivery_service.infrastructure.integration.telegram.const import (
    CREATE_SHOP_BTN,
    PRODUCTS_BTN,
)


def get_shop_staff_main_kbd(
    roles: list[Role],
) -> ReplyKeyboardMarkup:
    if Role.SHOP_OWNER in roles or Role.SHOP_MANAGER in roles:
        keyboard = [[KeyboardButton(text=PRODUCTS_BTN)]]
    else:
        keyboard = [[KeyboardButton(text=CREATE_SHOP_BTN)]]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
