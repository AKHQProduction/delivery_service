from dataclasses import dataclass

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.shop_gateway import (
    EmployeeFilters,
    EmployeeReadModel,
    ShopGateway,
)


@dataclass(frozen=True)
class GetEmployeesQuery:
    pagination: Pagination
    name: str | None = None


class GetEmployeesQueryHandler:
    def __init__(
        self, idp: IdentityProvider, shop_gateway: ShopGateway
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
