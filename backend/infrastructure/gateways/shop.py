from typing import Sequence

from sqlalchemy import RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.persistence.shop import (
    ShopGateway,
    ShopGatewayFilters,
    ShopReader,
)
from application.common.persistence.view_models import ShopView
from entities.shop.models import Shop, ShopId
from entities.user.models import UserId
from infrastructure.persistence.models.shop import shops_table
from infrastructure.persistence.models.user import users_table


class SQLAlchemyShopMapper(ShopGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def load_with_id(self, shop_id: ShopId) -> Shop | None:
        return await self.session.get(Shop, shop_id)

    async def load_with_identity(self, user_id: UserId) -> Shop | None:
        query = select(Shop).join(
            users_table, users_table.c.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def load_many(
        self, filters: ShopGatewayFilters | None = None
    ) -> Sequence[Shop]:
        query = select(Shop)

        if filters and filters.is_active:
            query = query.where(shops_table.c.is_active.is_(filters.is_active))

        result = await self.session.scalars(query)

        return result.all()


class SQLAlchemyShopReader(ShopReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_with_id(self, shop_id: ShopId) -> ShopView | None:
        query = select(
            shops_table.c.shop_title,
            shops_table.c.shop_delivery_distance,
            shops_table.c.shop_regular_days_off,
            shops_table.c.shop_special_days_off,
        ).where(shops_table.c.shop_id == shop_id)

        result = await self.session.execute(query)

        row: RowMapping | None = result.mappings().one_or_none()

        if not row:
            return None
        return ShopView(
            title=row.shop_title,
            delivery_distance=row.shop_delivery_distance,
            regular_days_off=row.shop_regular_days_off,
            special_days_off=row.shop_special_days_off,
        )
