from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.error import ApplicationError
from application.order.gateway import OrderItemSaver, OrderSaver
from entities.order.models import Order, OrderItem


class OrderGateway(OrderSaver, OrderItemSaver):
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
