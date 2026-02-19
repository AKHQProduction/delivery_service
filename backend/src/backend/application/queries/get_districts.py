from dataclasses import dataclass

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.district_gateway import (
    DistrictReadModel,
    GetDistrictsFilters,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyDistrictGateway,
)


@dataclass(frozen=True)
class GetDistrictsQuery:
    pagination: Pagination
    name: str | None = None


class GetDistrictsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        district_gateway: SQLAlchemyDistrictGateway,
    ) -> None:
        self._idp = idp
        self._district_gateway = district_gateway

    async def handle(
        self, query: GetDistrictsQuery
    ) -> list[DistrictReadModel]:
        current_user = await self._idp.current_user()

        return await self._district_gateway.read_all(
            filters=GetDistrictsFilters(
                name=query.name, shop_id=current_user.shop_id
            ),
            pagination=query.pagination,
        )
