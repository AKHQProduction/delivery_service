import logging
from dataclasses import dataclass

from application.common.input_data import Pagination
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.shop.gateway import ShopFilters, ShopReader


@dataclass
class SetupAllShop(Interactor[None, None]):
    _shop_reader: ShopReader
    _webhook_manager: WebhookManager

    async def __call__(self, data: None = None) -> None:
        shops = await self._shop_reader.all(
            filters=ShopFilters(is_active=True), pagination=Pagination()
        )

        total = await self._shop_reader.total(
            filters=ShopFilters(is_active=True)
        )

        for shop in shops:
            await self._webhook_manager.setup_webhook(shop.token)

        logging.info("All shops were launched, in total=%s", total)
