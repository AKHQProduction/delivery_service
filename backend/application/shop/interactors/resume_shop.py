import logging

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.transaction_manager import TransactionManager
from application.common.webhook_manager import WebhookManager
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import OldShopGateway
from application.user.errors import UserNotFoundError


class ResumeShop(Interactor[None, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: OldShopGateway,
        access_service: AccessService,
        commiter: TransactionManager,
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
            raise UserNotFoundError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if shop is None:
            raise UserNotHaveShopError(actor.user_id)

        await self._access_service.ensure_can_edit_shop(
            actor.user_id, shop.shop_id
        )

        shop.is_active = True

        await self._webhook_manager.setup_webhook(shop.token)

        await self._commiter.commit()

        logging.info(
            "ResumeShop: shop with id=%s resume its work", shop.shop_id
        )
