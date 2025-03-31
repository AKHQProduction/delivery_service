import logging
from dataclasses import dataclass, field

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_user
from application.common.webhook_manager import WebhookManager
from entities.shop.models import ShopId
from entities.shop.services import ShopService
from entities.shop.value_objects import ShopLocation


@dataclass(frozen=True)
class CreateShopCommand:
    title: str
    token: str
    delivery_distance: int
    location: tuple[float, float]
    regular_days_off: list[int] = field(default_factory=list)


@dataclass
class CreateShopCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    shop_service: ShopService
    access_service: AccessService
    webhook_manager: WebhookManager
    transaction_manager: TransactionManager

    async def __call__(self, command: CreateShopCommand) -> ShopId:
        location = ShopLocation(
            latitude=command.location[0], longitude=command.location[1]
        )

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        await self.access_service.ensure_can_create_shop(actor.oid)

        await self.webhook_manager.setup_webhook(command.token)

        new_shop = self.shop_service.create_shop(
            command.title,
            command.token,
            command.regular_days_off,
            command.delivery_distance,
            location,
            actor,
        )

        await self.transaction_manager.commit()

        logging.info(
            "CreateShop: User=%s created shop=%s", actor.oid, new_shop.oid
        )

        return new_shop.oid
