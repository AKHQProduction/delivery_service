import asyncio
import logging
from dataclasses import dataclass

from application.common.persistence.shop import (
    ShopGateway,
    ShopGatewayFilters,
)
from application.common.webhook_manager import WebhookManager


@dataclass
class SetupAllShopCommand:
    shop_gateway: ShopGateway
    webhook_manager: WebhookManager

    async def __call__(self) -> None:
        filters = ShopGatewayFilters(is_active=True)

        shops = await self.shop_gateway.load_many(filters=filters)
        total_shops = len(shops)

        logging.info("Found %s active shops", total_shops)

        setup_tasks = [
            self.webhook_manager.setup_webhook(shop.token) for shop in shops
        ]
        await asyncio.gather(*setup_tasks)

        logging.info("All shops were launched, in total=%s", total_shops)
