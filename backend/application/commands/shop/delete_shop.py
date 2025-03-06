import logging

from application.common.access_service import AccessService
from application.common.file_manager import FileManager
from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from application.common.webhook_manager import WebhookManager
from entities.shop.services import ShopService


class DeleteShopCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    shop_service: ShopService
    access_service: AccessService
    transaction_manager: TransactionManager
    webhook_manager: WebhookManager
    file_manager: FileManager

    async def __call__(self, data: None = None) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_delete_shop(actor.oid, shop.oid)

        await self.shop_service.delete_shop(shop)

        self.file_manager.delete_folder(str(shop.oid))

        await self.webhook_manager.drop_webhook(shop.token)
        await self.transaction_manager.commit()

        logging.info("DeleteShop: Successfully delete shop=%s", shop.oid)
