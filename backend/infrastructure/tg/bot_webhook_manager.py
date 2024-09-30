from aiogram import Bot

from application.common.webhook_manager import WebhookManager
from entities.shop.value_objects import ShopToken
from infrastructure.tg.config import WebhookConfig


class BotWebhookManager(WebhookManager):
    def __init__(self, config: WebhookConfig):
        self._config = config

    async def setup_webhook(self, token: ShopToken):
        async with Bot(token=token.value) as bot:
            await bot.delete_webhook(drop_pending_updates=True)

            bot_path = self._config.webhook_shop_path.format(
                bot_token=token.value
            )

            await bot.set_webhook(f"{self._config.webhook_url}{bot_path}")

    async def drop_webhook(self, token: ShopToken):
        async with Bot(token=token.value) as bot:
            await bot.delete_webhook()
