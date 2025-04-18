from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from delivery_service.domain.staff.staff_role import Role
from delivery_service.infrastructure.integration.telegram.const import (
    CREATE_SHOP_BTN,
    CUSTOMERS_BTN,
    ORDERS_BTN,
    PRODUCTS_BTN,
    STAFF_BTN,
)


def get_shop_staff_main_kbd(
    roles: list[Role],
) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    if Role.SHOP_OWNER in roles or Role.SHOP_MANAGER in roles:
        keyboard = [
            [KeyboardButton(text=PRODUCTS_BTN)],
            [KeyboardButton(text=CUSTOMERS_BTN)],
            [KeyboardButton(text=ORDERS_BTN)],
        ]

        if Role.SHOP_OWNER in roles:
            keyboard[1].insert(0, KeyboardButton(text=STAFF_BTN))
    elif Role.COURIER in roles:
        return ReplyKeyboardRemove()
    else:
        keyboard = [[KeyboardButton(text=CREATE_SHOP_BTN)]]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
