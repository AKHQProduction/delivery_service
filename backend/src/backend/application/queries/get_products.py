from dataclasses import dataclass

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.product_gateway import (
    GetProductsFilters,
    ProductGateway,
    ProductReadModel,
)


@dataclass(frozen=True)
class GetProductQuery:
    pagination: Pagination
    name: str | None = None


class GetProductsQueryHandler:
    def __init__(
        self, idp: IdentityProvider, product_gateway: ProductGateway
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
