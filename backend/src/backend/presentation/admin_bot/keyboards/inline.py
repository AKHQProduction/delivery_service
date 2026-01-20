from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def shop_kb(bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ Панель",
                    url=f"https://t.me/{bot_username}?startapp",
                )
            ]
        ]
    )
