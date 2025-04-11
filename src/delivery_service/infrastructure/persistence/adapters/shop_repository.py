from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.repository import ShopRepository
from delivery_service.domain.shops.shop import Shop
from delivery_service.infrastructure.persistence.tables import SHOPS_TABLE
from delivery_service.infrastructure.persistence.tables.shops import (
    STAFF_MEMBERS_TABLE,
)


class SQLAlchemyShopRepository(ShopRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, shop: Shop) -> None:
        self._session.add(shop)

    async def exists(self, identity_id: UserID) -> bool:
        query = select(
            exists()
            .select_from(
                SHOPS_TABLE.join(
                    STAFF_MEMBERS_TABLE,
                    SHOPS_TABLE.c.id == STAFF_MEMBERS_TABLE.c.shop_id,
                )
            )
            .where(and_(STAFF_MEMBERS_TABLE.c.user_id == identity_id))
        )
        result = await self._session.execute(query)
        return bool(result.scalar())

    async def load_with_identity(self, identity_id: UserID) -> Shop | None:
        query = select(Shop).join(
            STAFF_MEMBERS_TABLE,
            and_(STAFF_MEMBERS_TABLE.c.user_id == identity_id),
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def load_with_id(self, shop_id: ShopID) -> Shop | None:
        return await self._session.get(Shop, shop_id)
