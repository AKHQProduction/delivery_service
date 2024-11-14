import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopGateway
from application.user.gateway import UserSaver
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop
from entities.user.models import UserId
from entities.user.services import create_user


@dataclass(frozen=True)
class ShopBotStartInputData:
    shop_id: int
    user_id: int
    full_name: str
    username: str | None


class ShopBotStart(Interactor[ShopBotStartInputData, UserId]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_saver: UserSaver,
        shop_reader: ShopGateway,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._user_saver = user_saver
        self._shop_reader = shop_reader
        self._commiter = commiter

    async def __call__(self, data: ShopBotStartInputData) -> UserId:
        actor = await self._identity_provider.get_user()
        if actor:
            return actor.user_id

        shop = await self._shop_reader.by_id(ShopId(data.shop_id))
        if not shop:
            raise ShopNotFoundError(data.shop_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(data.shop_id)

        user = create_user(
            UserId(data.user_id),
            full_name=data.full_name,
            username=data.username,
        )

        add_user_to_shop(shop, user)

        await self._user_saver.save(user)

        await self._commiter.commit()

        logging.info("New user created, with_id=%s", user.user_id)

        return user.user_id
