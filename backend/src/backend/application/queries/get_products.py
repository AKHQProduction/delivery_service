from dataclasses import dataclass

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.product_gateway import (
    GetProductsFilters,
    ProductReadModel,
    ProductSummaryReadModel,
)
from backend.application.vars import CategoryId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)


@dataclass(frozen=True)
class GetProductsQuery:
    pagination: Pagination
    name: str | None = None
    category_id: CategoryId | None = None


@dataclass(frozen=True)
class GetProductSummaryQuery:
    name: str | None = None


class GetProductsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway

    async def handle(self, query: GetProductsQuery) -> list[ProductReadModel]:
        current_user = await self._idp.current_user()

        return await self._product_gateway.read_all(
            filters=GetProductsFilters(
                name=query.name,
                shop_id=current_user.shop_id,
                category_id=query.category_id,
            ),
            pagination=query.pagination,
        )

    async def summary(
        self, query: GetProductSummaryQuery
    ) -> ProductSummaryReadModel:
        current_user = await self._idp.current_user()

        return await self._product_gateway.read_summary(
            filters=GetProductsFilters(
                name=query.name,
                shop_id=current_user.shop_id,
            ),
        )
