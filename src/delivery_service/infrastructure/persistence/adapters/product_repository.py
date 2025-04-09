from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.products.product import Product
from delivery_service.domain.products.repository import ProductRepository
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.infrastructure.persistence.tables import PRODUCTS_TABLE


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, product: Product) -> None:
        self._session.add(product)

    async def exists(self, title: str, shop_id: ShopID) -> bool:
        query = select(
            exists().where(
                and_(
                    PRODUCTS_TABLE.c.title == title,
                    PRODUCTS_TABLE.c.shop_id == shop_id,
                )
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())
