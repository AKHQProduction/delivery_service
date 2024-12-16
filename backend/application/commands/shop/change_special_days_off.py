import logging
from dataclasses import dataclass
from datetime import date

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from entities.shop.value_objects import SpecialDaysOff


@dataclass(frozen=True)
class ChangeSpecialDaysOffCommand:
    special_days_off: list[date]


class ChangeSpecialDaysOffCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    transaction_manager: TransactionManager
    access_service: AccessService

    async def __call__(self, data: ChangeSpecialDaysOffCommand) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_edit_shop(actor.oid, shop.oid)

        shop.special_days_off = SpecialDaysOff(data.special_days_off)

        await self.transaction_manager.commit()

        logging.info(
            "ChangeSpecialDaysOff: successfully change regular days off "
            "for shop=%s",
            shop.oid,
        )
