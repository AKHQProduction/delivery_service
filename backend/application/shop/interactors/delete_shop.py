import logging

from application.common.access_service import AccessService
from application.common.file_manager import FileManager
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.transaction_manager import TransactionManager
from application.common.webhook_manager import WebhookManager
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import OldShopGateway, ShopSaver
from application.user.errors import UserNotFoundError


class DeleteShop(Interactor[None, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: OldShopGateway,
        shop_saver: ShopSaver,
        access_service: AccessService,
        commiter: TransactionManager,
        webhook_manager: WebhookManager,
        file_manager: FileManager,
    ):
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._shop_saver = shop_saver
        self._access_service = access_service
        self._commiter = commiter
        self._webhook_manager = webhook_manager
        self._file_manager = file_manager

    async def __call__(self, data: None = None) -> None:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if shop is None:
            raise UserNotHaveShopError(actor.user_id)

        shop_id = shop.shop_id

        await self._access_service.ensure_can_delete_shop(
            actor.user_id, shop_id
        )

        await self._shop_saver.delete(shop_id)

        self._file_manager.delete_folder(str(shop_id))

        await self._webhook_manager.drop_webhook(shop.token)

        await self._commiter.commit()

        logging.info("DeleteShop: Successfully delete shop=%s", shop_id)
