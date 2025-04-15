import logging
from collections.abc import Sequence
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.ports.product_gateway import (
    ProductGateway,
    ProductGatewayFilters,
    ProductReadModel,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shop_catalogs.repository import (
    ShopCatalogRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetAllProductsResponse:
    products: Sequence[ProductReadModel]
    total: int


@dataclass(frozen=True)
class GetAllProductsRequest(TelegramRequest[GetAllProductsResponse]):
    pass


class GetAllProductsHandler(
    RequestHandler[GetAllProductsRequest, GetAllProductsResponse]
):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_catalog: ShopCatalogRepository,
        product_gateway: ProductGateway,
    ) -> None:
        self._idp = idp
        self._shop_catalog = shop_catalog
        self._product_gateway = product_gateway

    async def handle(
        self, request: GetAllProductsRequest
    ) -> GetAllProductsResponse:
        logger.info("Request to get all products")
        current_user_id = await self._idp.get_current_user_id()

        shop_catalog = await self._shop_catalog.load_with_identity(
            identity_id=current_user_id
        )
        if not shop_catalog:
            raise AccessDeniedError()

        filters = ProductGatewayFilters(shop_id=shop_catalog.id)
        products = await self._product_gateway.read_all_products(
            filters=filters
        )
        total = await self._product_gateway.total(filters=filters)

        return GetAllProductsResponse(products=products, total=total)
