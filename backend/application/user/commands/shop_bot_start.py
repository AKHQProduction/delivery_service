import logging
from dataclasses import dataclass

from application.common.identity_provider import IdentityProvider
from application.common.interfaces.user.gateways import UserGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators.shop import validate_shop
from application.shop.gateway import OldShopGateway
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
    user_mapper: UserGateway
    shop_reader: OldShopGateway
    commiter: TransactionManager
    shop_service: ShopService

    async def __call__(self, data: ShopBotStartInputData) -> None:
        shop = await self.shop_reader.by_id(ShopId(data.shop_id))
        validate_shop(shop)

        if actor := await self.identity_provider.get_user():
            return self.shop_service.add_user_to_shop(shop, actor)

        new_user = self.user_service.create_new_user(
            full_name=data.full_name, username=data.username, tg_id=data.tg_id
        )

        self.shop_service.add_user_to_shop(shop, actor)

        await self.commiter.commit()

        logging.info("New user created, with_id=%s", new_user.oid)

        return None
