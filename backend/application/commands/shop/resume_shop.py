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
class ResumeShopCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    shop_service: ShopService
    access_service: AccessService
    transaction_manager: TransactionManager
    webhook_manager: WebhookManager

    async def __call__(self, data: None = None) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_edit_shop(actor.oid, shop.oid)

        self.shop_service.change_shop_activity(shop, is_active=True)
        await self.webhook_manager.setup_webhook(shop.token)

        await self.transaction_manager.commit()

        logging.info("ResumeShop: shop with id=%s resume its work", shop.oid)
