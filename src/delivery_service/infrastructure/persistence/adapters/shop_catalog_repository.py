from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.products.catalog import ShopCatalog
from delivery_service.domain.products.repository import ShopCatalogRepository
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables.shops import (
    STAFF_MEMBERS_TABLE,
)


class SQLAlchemyShopCatalogRepository(ShopCatalogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_identity(
        self, identity_id: UserID
    ) -> ShopCatalog | None:
        query = select(ShopCatalog).join(
            STAFF_MEMBERS_TABLE,
            and_(STAFF_MEMBERS_TABLE.c.user_id == identity_id),
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
