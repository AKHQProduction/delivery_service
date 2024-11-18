import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interfaces.user.gateways import UserMapper
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopGateway
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop
from entities.user.models import UserId
from entities.user.services import create_user


@dataclass(frozen=True)
class ShopBotStartInputData:
    shop_id: int
    tg_id: int
    full_name: str
    username: str | None


@dataclass
class ShopBotStart:
    identity_provider: IdentityProvider
    user_mapper: UserMapper
    shop_reader: ShopGateway
    commiter: Commiter

    async def __call__(self, data: ShopBotStartInputData) -> UserId:
        logging.info("Handle start command from shop bot")
        if actor := await self.identity_provider.get_user():
            return actor.user_id

        shop = await self.shop_reader.by_id(ShopId(data.shop_id))
        if not shop:
            raise ShopNotFoundError(data.shop_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(data.shop_id)

        new_user = create_user(
            full_name=data.full_name, username=data.username, tg_id=data.tg_id
        )

        add_user_to_shop(shop, new_user)

        await self.user_mapper.add_one(new_user)
        await self.commiter.commit()

        logging.info("New user created, with_id=%s", new_user.user_id)

        return new_user.user_id
