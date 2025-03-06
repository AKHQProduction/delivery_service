import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from application.common.webhook_manager import WebhookManager
from entities.shop.services import ShopService


@dataclass
class StopShopCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    shop_service: ShopService
    access_service: AccessService
    transaction_manager: TransactionManager
    webhook_manager: WebhookManager

    async def __call__(self) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_edit_shop(actor.oid, shop.oid)

        self.shop_service.change_shop_activity(shop, is_active=False)

        await self.webhook_manager.drop_webhook(shop.token)
        await self.transaction_manager.commit()

        logging.info("StopShop: shop with id=%s messed up its work", shop.oid)
