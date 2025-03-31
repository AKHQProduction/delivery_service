from dataclasses import dataclass
from decimal import Decimal

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.application.errors import ShopNotFoundError
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider

# ruff: noqa: E501
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.domain.products.product import (
    ProductID,
    ProductType,
)
from delivery_service.domain.products.repository import (
    ProductRepository,
    ShopCatalogRepository,
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
        id_generator: IDGenerator,
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
        )

        self._product_repository.add(new_product)
        await self._transaction_manager.commit()

        return new_product.entity_id
