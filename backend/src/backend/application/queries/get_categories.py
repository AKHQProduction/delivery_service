from dataclasses import dataclass

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.category_gateway import (
    CategoryReadModel,
    GetCategoriesFilters,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyCategoryGateway,
)


@dataclass(frozen=True)
class GetCategoriesQuery:
    pagination: Pagination
    name: str | None = None


class GetCategoriesQueryHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        category_gateway: SQLAlchemyCategoryGateway,
    ) -> None:
        self._idp = idp
        self._category_gateway = category_gateway

    async def handle(
        self, query: GetCategoriesQuery
    ) -> list[CategoryReadModel]:
        current_user = await self._idp.current_user()

        return await self._category_gateway.read_all(
            filters=GetCategoriesFilters(
                name=query.name, shop_id=current_user.shop_id
            ),
            pagination=query.pagination,
        )
