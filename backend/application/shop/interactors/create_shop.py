import logging
from dataclasses import dataclass, field

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.gateway import ShopSaver
from application.user.gateway import UserSaver
from entities.shop.models import ShopId
from entities.shop.services import ShopService


@dataclass(frozen=True)
class CreateShopDTO:
    shop_id: int
    title: str
    token: str
    regular_days_off: list[int] = field(default_factory=list)


class CreateShop(Interactor[CreateShopDTO, ShopId]):
    def __init__(
            self,
            shop_saver: ShopSaver,
            user_saver: UserSaver,
            commiter: Commiter,
            identity_provider: IdentityProvider,
            shop_service: ShopService

    ) -> None:
        self._shop_saver = shop_saver
        self._user_saver = user_saver
        self._commiter = commiter
        self._identity_provider = identity_provider
        self._shop_service = shop_service

    async def __call__(self, data: CreateShopDTO) -> ShopId:
        user = await self._identity_provider.get_user()

        shop = await self._shop_service.create_shop(
                user,
                data.shop_id,
                data.title,
                data.token,
                data.regular_days_off
        )

        await self._shop_saver.save(shop)
        await self._commiter.commit()

        logging.info(f"CreateShop: New shop created with id={data.shop_id}")
        logging.info(
                f"CreateShop: Add user={user.user_id} to shop={shop.shop_id}"
        )

        return shop.shop_id
