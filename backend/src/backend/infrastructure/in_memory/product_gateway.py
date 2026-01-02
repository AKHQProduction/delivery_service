import asyncio
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
from backend.infrastructure.in_memory.category_gateway import (
    InMemoryCategoryGateway,
)


class InMemoryProductGateway(ProductGateway):
    def __init__(
        self, category_gateway: InMemoryCategoryGateway | None = None
    ) -> None:
        self.products: dict[ProductId, Product] = {}
        self.updated = False
        self._category_gateway = category_gateway

    async def create_product(self, dto: CreateProductDTO) -> None:
        product = Product(
            product_id=dto.product_id,
            shop_id=dto.shop_id,
            name=dto.name,
            price=dto.price,
            category_id=dto.category_id,
        )
        self.products.setdefault(dto.product_id, product)

    async def load(self, product_id: ProductId) -> Product | None:
        return self.products.get(product_id)

    async def load_many(self, product_ids: list[ProductId]) -> list[Product]:
        return [
            product
            for pid in product_ids
            if (product := self.products.get(pid)) is not None
        ]

    async def _get_category_name(self, product: Product) -> str | None:
        if not product.category_id or not self._category_gateway:
            return None
        category = await self._category_gateway.load(product.category_id)
        return category.name if category else None

    async def read(
        self, product_id: ProductId, shop_id: ShopId
    ) -> ProductReadModel | None:
        product = self.products.get(product_id)
        if product:
            return ProductReadModel(
                product_id=product_id,
                name=product.name,
                price=product.price,
                category_id=product.category_id,
                category_name=await self._get_category_name(product),
            )
        return None

    async def read_all(
        self, filters: GetProductsFilters, pagination: Pagination
    ) -> list[ProductReadModel]:
        filtered_products = list(self.products.values())

        if filters.shop_id:
            filtered_products = [
                p for p in filtered_products if p.shop_id == filters.shop_id
            ]
        if filters.name:
            filtered_products = [
                p
                for p in filtered_products
                if filters.name.lower() in p.name.lower()
            ]

        if pagination.order == SortOrder.ASC:
            filtered_products.sort(key=lambda p: p.name)
        else:
            filtered_products.sort(key=lambda p: p.name, reverse=True)

        start = pagination.offset
        end = start + pagination.limit
        paginated_products = filtered_products[start:end]

        category_names = await asyncio.gather(*[
            self._get_category_name(product) for product in paginated_products
        ])
        return [
            ProductReadModel(
                product_id=product.product_id,
                name=product.name,
                price=product.price,
                category_id=product.category_id,
                category_name=category_name,
            )
            for product, category_name in zip(
                paginated_products, category_names, strict=True
            )
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
