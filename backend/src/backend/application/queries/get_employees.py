from dataclasses import dataclass

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.shop_gateway import (
    EmployeeFilters,
    EmployeeReadModel,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway


@dataclass(frozen=True)
class GetEmployeesQuery:
    pagination: Pagination
    name: str | None = None


class GetEmployeesQueryHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway

    async def handle(
        self, query: GetEmployeesQuery
    ) -> list[EmployeeReadModel]:
        current_user = await self._idp.current_user()

        return await self._shop_gateway.read_all_employees(
            filters=EmployeeFilters(
                name=query.name, shop_id=current_user.shop_id
            ),
            pagination=query.pagination,
        )
