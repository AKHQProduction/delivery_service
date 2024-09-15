import logging
from dataclasses import dataclass
from datetime import datetime

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError
from entities.shop.value_objects import SpecialDaysOff


@dataclass(frozen=True)
class ChangeSpecialDaysOffInputData:
    special_days_off: list[datetime]


class ChangeSpecialDaysOff(Interactor[ChangeSpecialDaysOffInputData, None]):
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

    async def __call__(self, data: ChangeSpecialDaysOffInputData) -> None:
        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserIsNotExistError()

        shop = await self._shop_reader.by_identity(actor.user_id)

        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        shop_id = shop.shop_id

        await self._access_service.ensure_can_edit_shop(actor.user_id, shop_id)

        shop.special_days_off = SpecialDaysOff(data.special_days_off)

        await self._commiter.commit()

        logging.info(
            "ChangeSpecialDaysOff: successfully change regular days off "
            "for shop=%s",
            shop_id,
        )
