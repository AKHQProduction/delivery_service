import logging
from dataclasses import dataclass

from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop
from entities.shop.models import ShopId
from entities.shop.services import ShopService
from entities.user.services import UserService


@dataclass(frozen=True)
class ShopBotStartInputData:
    shop_id: int
    tg_id: int
    full_name: str
    username: str | None


@dataclass
class ShopBotStart:
    identity_provider: IdentityProvider
    user_service: UserService
    shop_service: ShopService
    shop_gateway: ShopGateway
    transaction_manager: TransactionManager

    async def __call__(self, data: ShopBotStartInputData) -> None:
        shop = await self.shop_gateway.load_with_id(ShopId(data.shop_id))
        validate_shop(shop)

        if actor := await self.identity_provider.get_user():
            return self.shop_service.add_user_to_shop(shop, actor)

        new_user = self.user_service.create_new_user(
            full_name=data.full_name, username=data.username, tg_id=data.tg_id
        )

        self.shop_service.add_user_to_shop(shop, actor)

        await self.transaction_manager.commit()

        logging.info("New user created, with_id=%s", new_user.oid)

        return None
