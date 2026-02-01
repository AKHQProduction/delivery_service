from dataclasses import dataclass

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.product_gateway import (
    GetProductsFilters,
    ProductReadModel,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)


@dataclass(frozen=True)
class GetProductQuery:
    pagination: Pagination
    name: str | None = None


class GetProductsQueryHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        product_gateway: SQLAlchemyProductGateway,
    ) -> None:
        self._idp = idp
        self._product_gateway = product_gateway

    async def handle(self, query: GetProductQuery) -> list[ProductReadModel]:
        current_user = await self._idp.current_user()

        return await self._product_gateway.read_all(
            filters=GetProductsFilters(
                name=query.name, shop_id=current_user.shop_id
            ),
            pagination=query.pagination,
        )
