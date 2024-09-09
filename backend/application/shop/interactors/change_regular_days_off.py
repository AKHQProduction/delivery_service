import logging
from dataclasses import dataclass, field

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.interactor import Interactor
from application.shop.errors import ShopIsNotExistError
from application.shop.gateway import ShopReader

from entities.shop.models import ShopId
from entities.shop.value_objects import RegularDaysOff


@dataclass(frozen=True)
class ChangeRegularDaysOffRequestData:
    shop_id: int
    regular_days_off: list[int] = field(default_factory=list)


class ChangeRegularDaysOff(Interactor[ChangeRegularDaysOffRequestData, None]):
    def __init__(
            self,
            shop_reader: ShopReader,
            commiter: Commiter,
            access_service: AccessService
    ) -> None:
        self._shop_reader = shop_reader
        self._commiter = commiter
        self._access_service = access_service

    async def __call__(self, data: ChangeRegularDaysOffRequestData) -> None:
        shop_id = ShopId(data.shop_id)

        shop = await self._shop_reader.by_id(shop_id)

        if not shop:
            raise ShopIsNotExistError(shop_id)

        await self._access_service.ensure_can_edit_shop(shop_id)

        shop.regular_days_off = RegularDaysOff(data.regular_days_off)

        await self._commiter.commit()

        logging.info(
                "ChangeRegularDaysOff: successfully change regular days off "
                f"for shop={data.shop_id}"
        )
