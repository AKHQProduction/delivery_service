import logging
from dataclasses import dataclass, field

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.shop.errors import ShopIsNotExistsError
from application.shop.gateway import ShopReader

from entities.shop.models import ShopId
from entities.shop.value_objects import RegularDaysOff


@dataclass(frozen=True)
class ChangeRegularDaysOffDTO:
    shop_id: int
    regular_days_off: list[int] = field(default_factory=list)


class ChangeRegularDaysOff(Interactor[ChangeRegularDaysOffDTO, None]):
    def __init__(
            self,
            identity_provider: IdentityProvider,
            shop_reader: ShopReader,
            commiter: Commiter,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._commiter = commiter

    async def __call__(self, data: ChangeRegularDaysOffDTO) -> None:
        shop = await self._shop_reader.by_id(ShopId(data.shop_id))

        if not shop:
            raise ShopIsNotExistsError(data.shop_id)

        shop.regular_days_off = RegularDaysOff(data.regular_days_off)

        await self._commiter.commit()

        logging.info(
                "ChangeRegularDaysOff: successfully change regular days off "
                f"for shop={data.shop_id}"
        )
