import logging

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError


class StopShop(Interactor[None, None]):
    def __init__(
            self,
            identity_provider: IdentityProvider,
            shop_reader: ShopReader,
            access_service: AccessService,
            commiter: Commiter,
            webhook_manager: WebhookManager,

    ):
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._access_service = access_service
        self._commiter = commiter
        self._webhook_manager = webhook_manager

    async def __call__(self, data: None = None) -> None:
        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserIsNotExistError()

        shop = await self._shop_reader.by_identity(actor.user_id)

        if shop is None:
            raise UserNotHaveShopError(actor.user_id)

        await self._access_service.ensure_can_edit_shop(shop.shop_id)

        shop.is_active = False

        await self._webhook_manager.drop_webhook(shop.token.value)

        await self._commiter.commit()

        logging.info(
                f"StopShop: shop with id={shop.shop_id} messed up its work"
        )
