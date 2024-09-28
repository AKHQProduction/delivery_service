import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserNotFoundError
from entities.shop.value_objects import RegularDaysOff


@dataclass(frozen=True)
class ChangeRegularDaysOffInputData:
    regular_days_off: list[int]


class ChangeRegularDaysOff(Interactor[ChangeRegularDaysOffInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: ShopReader,
        commiter: Commiter,
        access_service: AccessService,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._commiter = commiter
        self._access_service = access_service

    async def __call__(self, data: ChangeRegularDaysOffInputData) -> None:
        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserNotFoundError()

        shop = await self._shop_reader.by_identity(actor.user_id)

        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        shop_id = shop.shop_id

        await self._access_service.ensure_can_edit_shop(actor.user_id, shop_id)

        shop.regular_days_off = RegularDaysOff(data.regular_days_off)

        await self._commiter.commit()

        logging.info(
            "ChangeRegularDaysOff: successfully change regular days off "
            "for shop=%s",
            shop_id,
        )
