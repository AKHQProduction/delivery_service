import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.shop.errors import ShopIsNotExistError
from application.shop.gateway import ShopReader
from entities.shop.models import ShopId


@dataclass(frozen=True)
class StopShopRequestData:
    shop_id: int


class StopShop(Interactor[StopShopRequestData, None]):
    def __init__(
            self,
            shop_reader: ShopReader,
            access_service: AccessService,
            commiter: Commiter,
            webhook_manager: WebhookManager,

    ):
        self._shop_reader = shop_reader
        self._access_service = access_service
        self._commiter = commiter
        self._webhook_manager = webhook_manager

    async def __call__(self, data: StopShopRequestData) -> None:
        shop = await self._shop_reader.by_id(ShopId(data.shop_id))

        if shop is None:
            raise ShopIsNotExistError(data.shop_id)

        await self._access_service.ensure_can_edit_shop(shop.shop_id)

        shop.is_active = False

        await self._webhook_manager.drop_webhook(shop.token.value)

        await self._commiter.commit()

        logging.info(
                f"StopShop: shop with id={shop.shop_id} messed up its work"
        )
