import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.shop.errors import ShopIsNotExistError
from application.shop.gateway import ShopReader, ShopSaver
from entities.shop.models import ShopId


@dataclass(frozen=True)
class DeleteShopRequestData:
    shop_id: int


class DeleteShop(Interactor[DeleteShopRequestData, None]):
    def __init__(
            self,
            shop_reader: ShopReader,
            shop_saver: ShopSaver,
            access_service: AccessService,
            commiter: Commiter,
            webhook_manager: WebhookManager,

    ):
        self._shop_reader = shop_reader
        self._shop_saver = shop_saver
        self._access_service = access_service
        self._commiter = commiter
        self._webhook_manager = webhook_manager

    async def __call__(self, data: DeleteShopRequestData) -> None:
        shop_id = ShopId(data.shop_id)

        shop = await self._shop_reader.by_id(shop_id)

        if shop is None:
            raise ShopIsNotExistError(shop_id)

        await self._access_service.ensure_can_delete_shop(shop_id)

        await self._shop_saver.delete(shop_id)

        await self._webhook_manager.drop_webhook(shop.token.value)

        await self._commiter.commit()

        logging.info(f"DeleteShop: Successfully delete shop={shop_id}")
