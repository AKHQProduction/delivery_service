from uuid import UUID

from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    GetProductsFilters,
    Product,
    ProductGateway,
    ProductReadModel,
)
from backend.application.vars import ProductId, ShopId


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

    async def read(
        self, product_id: ProductId, shop_id: ShopId
    ) -> ProductReadModel | None:
        product = self.products.get(product_id)
        if product:
            return ProductReadModel(
                product_id=product_id,
                name=product.name,
                price=product.price,
                category=product.category,
            )
        return None

    async def read_all(
        self, filters: GetProductsFilters, pagination: Pagination
    ) -> list[ProductReadModel]:
        # Filter by name
        filtered_products = [
            product
            for product in self.products.values()
            if filters.name and filters.name.lower() in product.name.lower()
        ]

        # Sort by name
        if pagination.order == SortOrder.ASC:
            filtered_products.sort(key=lambda p: p.name)
        else:
            filtered_products.sort(key=lambda p: p.name, reverse=True)

        # Apply pagination
        start = pagination.offset
        end = start + pagination.limit
        paginated_products = filtered_products[start:end]

        # Convert to ProductReadModel
        return [
            ProductReadModel(
                product_id=product.product_id,
                name=product.name,
                price=product.price,
                category=product.category,
            )
            for product in paginated_products
        ]

    async def update(self, updated_product: Product) -> None:
        if updated_product.product_id in self.products:
            self.products[updated_product.product_id] = updated_product
            self.updated = True

    async def delete(self, product_id: ProductId) -> None:
        if product_id in self.products:
            del self.products[product_id]

    def next_id(self) -> ProductId:
        return ProductId(UUID(str(uuid7())))
