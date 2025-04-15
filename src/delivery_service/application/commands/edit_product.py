import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    ProductNotFoundError,
    ShopNotFoundError,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.products.product import ProductID
from delivery_service.domain.products.repository import ProductRepository
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shop_catalogs.repository import (
    ShopCatalogRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditProductTitleRequest(TelegramRequest[None]):
    product_id: ProductID
    new_title: str


class EditProductTitleHandler(RequestHandler[EditProductTitleRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_catalog_repository: ShopCatalogRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._idp = idp
        self._shop_catalog_repository = shop_catalog_repository
        self._product_repository = product_repository

    async def handle(self, request: EditProductTitleRequest) -> None:
        logger.info("Request to edit product title")
        current_user_id = await self._idp.get_current_user_id()

        shop_catalog = await self._shop_catalog_repository.load_with_identity(
            current_user_id
        )
        if not shop_catalog:
            raise ShopNotFoundError()
        product = await self._product_repository.load_with_id(
            request.product_id
        )
        if not product:
            raise ProductNotFoundError()

        shop_catalog.edit_product_title(
            request.new_title, product, current_user_id
        )


@dataclass(frozen=True)
class EditProductPriceRequest(TelegramRequest[None]):
    product_id: ProductID
    new_price: FixedDecimal


class EditProductPriceHandler(RequestHandler[EditProductPriceRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_catalog_repository: ShopCatalogRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._idp = idp
        self._shop_catalog_repository = shop_catalog_repository
        self._product_repository = product_repository

    async def handle(self, request: EditProductPriceRequest) -> None:
        logger.info("Request to edit product price")
        current_user_id = await self._idp.get_current_user_id()

        shop_catalog = await self._shop_catalog_repository.load_with_identity(
            current_user_id
        )
        if not shop_catalog:
            raise ShopNotFoundError()
        product = await self._product_repository.load_with_id(
            request.product_id
        )
        if not product:
            raise ProductNotFoundError()

        shop_catalog.edit_product_price(
            request.new_price, product, current_user_id
        )
