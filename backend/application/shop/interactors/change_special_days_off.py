import logging
from dataclasses import dataclass, field
from datetime import datetime

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.errors import ShopIsNotExistError
from application.shop.gateway import ShopReader
from entities.shop.models import ShopId


@dataclass(frozen=True)
class ChangeRegularDaysOffRequestData:
    shop_id: int
    special_days_off: list[datetime] = field(default_factory=list)


class ChangeRegularDaysOff(Interactor[ChangeRegularDaysOffRequestData, None]):
    def __init__(
            self,
            identity_provider: IdentityProvider,
            shop_reader: ShopReader,
            commiter: Commiter
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._commiter = commiter

    async def __call__(self, data: ChangeRegularDaysOffRequestData) -> None:
        shop = await self._shop_reader.by_id(ShopId(data.shop_id))

        if not shop:
            raise ShopIsNotExistError(data.shop_id)

        shop.special_days_off = data.special_days_off

        await self._commiter.commit()

        logging.info(
                "ChangeSpecialDaysOff: successfully change regular days off "
                f"for shop={data.shop_id}"
        )
