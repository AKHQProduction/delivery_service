# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import ShopNotFoundError
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.products.errors import ProductAlreadyExistsError
from delivery_service.domain.products.product import (
    ProductID,
    ProductType,
)
from delivery_service.domain.products.repository import (
    ProductRepository,
)
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.domain.shop_catalogs.repository import (
    ShopCatalogRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewProductRequest(TelegramRequest[ProductID]):
    title: str
    price: FixedDecimal
    product_type: ProductType


class AddNewProductHandler(RequestHandler[AddNewProductRequest, ProductID]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_catalog_repository: ShopCatalogRepository,
        id_generator: IDGenerator,
        product_repository: ProductRepository,
    ) -> None:
        self._idp = identity_provider
        self._shop_catalog_repository = shop_catalog_repository
        self._id_generator = id_generator
        self._product_repository = product_repository

    async def handle(self, request: AddNewProductRequest) -> ProductID:
        logger.info("Request to add new product")
        current_user_id = await self._idp.get_current_user_id()

        shop_catalog = await self._shop_catalog_repository.load_with_identity(
            current_user_id
        )
        if not shop_catalog:
            raise ShopNotFoundError()
        if await self._product_repository.exists(
            request.title, shop_catalog.id
        ):
            raise ProductAlreadyExistsError()

        product_id = self._id_generator.generate_product_id()
        new_product = shop_catalog.add_product(
            new_product_id=product_id,
            title=request.title,
            price=request.price,
            product_type=request.product_type,
            creator_id=current_user_id,
        )
        self._product_repository.add(new_product)

        return new_product.entity_id
