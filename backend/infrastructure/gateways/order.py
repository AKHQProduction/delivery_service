from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.error import ApplicationError
from application.order.gateway import (
    OrderItemReader,
    OrderItemSaver,
    OrderReader,
    OrderSaver,
)
from entities.order.models import Order, OrderId, OrderItem
from infrastructure.persistence.models.order import (
    order_items_table,
    orders_table,
)


class OrderGateway(OrderSaver, OrderItemSaver, OrderItemReader, OrderReader):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def save(self, order: Order) -> None:
        self.session.add(order)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise ApplicationError() from error

    async def save_items(self, order_items: list[OrderItem]) -> None:
        self.session.add_all(order_items)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise ApplicationError() from error

    async def by_id(self, order_id: OrderId) -> Order | None:
        query = select(Order).where(orders_table.c.order_id == order_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def by_order_id(self, order_id: OrderId) -> list[OrderItem]:
        query = select(OrderItem).where(
            order_items_table.c.order_id == order_id
        )

        result = await self.session.scalars(query)

        return list(result.all())
