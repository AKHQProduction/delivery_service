from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError

from application.common.webhook_manager import TokenVerifier, WebhookManager
from infrastructure.tg.config import WebhookConfig
from infrastructure.tg.errors import ShopTokenUnauthorizedError


class BotWebhookManager(WebhookManager, TokenVerifier):
    def __init__(self, config: WebhookConfig):
        self._config = config

    async def verify(self, token: str) -> None:
        async with Bot(token=token) as bot:
            try:
                await bot.get_me()
            except TelegramUnauthorizedError as error:
                raise ShopTokenUnauthorizedError(token) from error

    async def setup_webhook(self, token: str) -> None:
        await self.verify(token)

        async with Bot(token=token) as bot:
            await bot.delete_webhook(drop_pending_updates=True)

            bot_path = self._config.webhook_shop_path.format(bot_token=token)

            await bot.set_webhook(f"{self._config.webhook_url}{bot_path}")

    async def drop_webhook(self, token: str) -> None:
        async with Bot(token=token) as bot:
            await bot.delete_webhook()
