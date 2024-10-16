import asyncio
import logging
from dataclasses import dataclass

from application.common.input_data import Pagination
from application.common.webhook_manager import WebhookManager
from application.shop.gateway import ShopFilters, ShopReader


@dataclass
class SetupAllShop:
    shop_reader: ShopReader
    webhook_manager: WebhookManager

    async def __call__(self) -> None:
        filters = ShopFilters(is_active=True)

        shops = await asyncio.create_task(
            self.shop_reader.all(filters=filters, pagination=Pagination())
        )
        total_shop = await asyncio.create_task(
            self.shop_reader.total(filters=filters)
        )

        logging.info("Found %s active shops", total_shop)

        setup_tasks = [
            self.webhook_manager.setup_webhook(shop.token) for shop in shops
        ]
        await asyncio.gather(*setup_tasks)

        logging.info("All shops were launched, in total=%s", total_shop)
