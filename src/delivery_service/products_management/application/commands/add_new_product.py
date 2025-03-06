from dataclasses import dataclass
from decimal import Decimal

from bazario import Request
from bazario.asyncio import RequestHandler

# ruff: noqa: E501
from delivery_service.products_management.application.ports.id_generator import (
    ProductIDGenerator,
)
from delivery_service.products_management.domain.product import (
    ProductID,
    ProductType,
)
from delivery_service.products_management.domain.repository import (
    ProductRepository,
    ShopCatalogRepository,
)
from delivery_service.shared.application.ports.idp import IdentityProvider
from delivery_service.shared.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.shop_management.application.errors import (
    ShopNotFoundError,
)


@dataclass(frozen=True)
class AddNewProductRequest(Request[ProductID]):
    title: str
    price: Decimal
    product_type: ProductType


class AddNewProductHandler(RequestHandler[AddNewProductRequest, ProductID]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        catalog_repository: ShopCatalogRepository,
        id_generator: ProductIDGenerator,
        product_repository: ProductRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._idp = identity_provider
        self._catalog_repository = catalog_repository
        self._id_generator = id_generator
        self._product_repository = product_repository
        self._transaction_manager = transaction_manager

    async def handle(self, request: AddNewProductRequest) -> ProductID:
        current_user_id = await self._idp.get_current_user_id()

        catalog = await self._catalog_repository.load_with_identity(
            current_user_id
        )
        if not catalog:
            raise ShopNotFoundError()

        product_id = self._id_generator.generate_product_id()
        new_product = catalog.add_new_product(
            product_id=product_id,
            title=request.title,
            product_price=request.price,
            product_type=request.product_type,
            creator_id=current_user_id,
        )

        self._product_repository.add(new_product)
        await self._transaction_manager.commit()

        return new_product.entity_id
