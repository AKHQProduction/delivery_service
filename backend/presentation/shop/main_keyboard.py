from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from presentation.common.consts import (
    CREATE_ORDER_BTN_TXT,
    MY_ORDERS_BTN_TXT,
    PROFILE_BTN_TXT,
)


def main_menu_shop_bot() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=PROFILE_BTN_TXT)],
            [
                KeyboardButton(text=CREATE_ORDER_BTN_TXT),
                KeyboardButton(text=MY_ORDERS_BTN_TXT),
            ],
        ],
        resize_keyboard=True,
    )
