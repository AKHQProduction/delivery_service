from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from backend.bootstrap.config import WebhookConfig


def shop_kb(webhook_config: WebhookConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ Панель",
                    web_app=WebAppInfo(url=webhook_config.webhook_url),
                )
            ]
        ]
    )
