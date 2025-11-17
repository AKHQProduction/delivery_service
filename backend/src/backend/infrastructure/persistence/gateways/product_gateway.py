from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    ProductGateway,
)
from backend.application.vars import ProductId
from backend.infrastructure.persistence.tables import Product


class SQLAlchemyProductGateway(ProductGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> ProductId:
        return ProductId(UUID(str(uuid7())))

    async def create_product(self, dto: CreateProductDTO) -> None:
        self._session.add(
            Product(
                id=dto.product_id,
                shop_id=dto.shop_id,
                name=dto.name,
                price=dto.price,
                category=dto.category,
            )
        )
