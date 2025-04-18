from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.shop_gateway import (
    ShopGateway,
    ShopReadModel,
)
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shops.value_objects import DaysOff
from delivery_service.infrastructure.persistence.tables import SHOPS_TABLE


class SQLAlchemyShopGateway(ShopGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_with_id(self, shop_id: ShopID) -> ShopReadModel | None:
        query = select(SHOPS_TABLE.c.id, SHOPS_TABLE.c.days_off).where(
            and_(SHOPS_TABLE.c.id == shop_id)
        )

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        if row:
            days_off: DaysOff = row["days_off"]
            return ShopReadModel(
                shop_id=row["id"],
                regular_days_off=days_off.regular_days_off,
                irregular_days_off=days_off.irregular_days_off,
            )
        return None
