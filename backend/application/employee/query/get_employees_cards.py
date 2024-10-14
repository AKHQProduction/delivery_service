import logging
from dataclasses import dataclass
from typing import Iterable

from application.common.identity_provider import IdentityProvider
from application.common.input_data import Pagination
from application.employee.gateway import (
    EmployeeFilters,
    EmployeeReader,
)
from application.employee.output_data import EmployeeCard
from application.shop.errors import (
    ShopIsNotActiveError,
    UserNotHaveShopError,
)
from application.shop.gateway import ShopReader
from application.user.errors import UserNotFoundError


@dataclass(frozen=True)
class GetEmployeeCardsInputData:
    filters: EmployeeFilters
    pagination: Pagination


@dataclass
class GetEmployeeCardsOutputData:
    total: int
    employees_card: Iterable[EmployeeCard]


@dataclass(frozen=True)
class GetEmployeeCards:
    identity_provider: IdentityProvider
    shop_reader: ShopReader
    employee_reader: EmployeeReader

    async def __call__(
        self, data: GetEmployeeCardsInputData
    ) -> GetEmployeeCardsOutputData:
        actor = await self.identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        shop = await self.shop_reader.by_identity(actor.user_id)

        if not shop:
            raise UserNotHaveShopError(actor.user_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(shop.shop_id)

        filters = EmployeeFilters(shop_id=shop.shop_id)

        employee_cards = await self.employee_reader.all_cards(
            filters=filters, pagination=Pagination()
        )

        total = await self.employee_reader.total(filters=filters)

        logging.info("Get employee cards, total=%s", total)

        return GetEmployeeCardsOutputData(
            total=total, employees_card=employee_cards
        )
