from uuid import UUID

from uuid_utils import uuid7

from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    Product,
    ProductGateway,
)
from backend.application.vars import ProductId


class InMemoryProductGateway(ProductGateway):
    def __init__(self) -> None:
        self.products: dict[ProductId, Product] = {}
        self.updated = False

    async def create_product(self, dto: CreateProductDTO) -> None:
        product = Product(
            product_id=dto.product_id,
            shop_id=dto.shop_id,
            name=dto.name,
            price=dto.price,
            category=dto.category,
        )
        self.products.setdefault(dto.product_id, product)

    async def load(self, product_id: ProductId) -> Product | None:
        return self.products.get(product_id)

    async def update(self, updated_product: Product) -> None:
        if updated_product.product_id in self.products:
            self.products[updated_product.product_id] = updated_product
            self.updated = True

    async def delete(self, product_id: ProductId) -> None:
        if product_id in self.products:
            del self.products[product_id]

    def next_id(self) -> ProductId:
        return ProductId(UUID(str(uuid7())))
