from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.orders.order import Order
from delivery_service.domain.orders.repository import OrderRepository


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, new_order: Order) -> None:
        return self._session.add(new_order)
