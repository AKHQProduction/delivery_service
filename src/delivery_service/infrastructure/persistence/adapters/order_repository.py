from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.orders.order import Order
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.orders.repository import (
    OrderRepository,
)
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.infrastructure.persistence.tables import ORDERS_TABLE


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, new_order: Order) -> None:
        return self._session.add(new_order)

    async def load_many_with_shop_id(self, shop_id: ShopID) -> Sequence[Order]:
        query = select(Order).where(and_(ORDERS_TABLE.c.shop_id == shop_id))

        result = await self._session.execute(query)
        return result.scalars().all()

    async def load_with_id(self, order_id: OrderID) -> Order | None:
        return await self._session.get(Order, order_id)
