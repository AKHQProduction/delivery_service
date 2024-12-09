from sqlalchemy import RowMapping, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.shop.gateways import ShopGateway
from application.shop.gateway import (
    ShopInfo,
    ShopReader,
)
from entities.shop.models import ShopId
from infrastructure.persistence.models.shop import shops_table


class ShopMapper(ShopGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def is_exists(self, token: str) -> bool:
        query = select(exists()).where(shops_table.c.token == token)

        result = await self.session.execute(query)

        return result.scalar()


class SqlalchemyShopReader(ShopReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, shop_id: ShopId) -> ShopInfo | None:
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
        return ShopInfo(
            title=row.shop_title,
            delivery_distance=row.shop_delivery_distance,
            regular_days_off=row.shop_regular_days_off,
            special_days_off=row.shop_special_days_off,
        )
