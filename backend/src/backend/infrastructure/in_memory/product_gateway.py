from typing import Any
from uuid import UUID

from uuid_utils import uuid7

from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    ProductGateway,
)
from backend.application.vars import ProductId, ShopId


class InMemoryProductGateway(ProductGateway):
    def __init__(self) -> None:
        self.products: dict[ShopId, dict[ProductId, Any]] = {}

    async def create_product(self, dto: CreateProductDTO) -> None:
        self.products.setdefault(dto.shop_id, {dto.product_id: dto})

    def next_id(self) -> ProductId:
        return ProductId(UUID(str(uuid7())))
