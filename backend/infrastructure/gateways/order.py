from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.persistence.order import OrderGateway, OrderReader
from application.common.persistence.view_models import OrderItemView, OrderView
from entities.order.models import Order, OrderId, OrderItemId
from infrastructure.persistence.models.order import (
    order_items_table,
    orders_table,
)


class SQLAlchemyOrderMapper(OrderGateway):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def load_with_id(self, order_id: OrderId) -> Order | None:
        return await self.session.get(Order, order_id)

    async def load_with_item_id(
        self, order_item_id: OrderItemId
    ) -> Order | None:
        query = (
            select(Order)
            .join(
                order_items_table,
                and_(orders_table.c.order_id == order_items_table.c.order_id),
            )
            .where(order_items_table.c.order_item_id == order_item_id)
        )
        result = await self.session.execute(query)

        return result.scalars().one_or_none()


class SQLAlchemyOrderReader(OrderReader):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def read_with_id(self, order_id: OrderId) -> OrderView | None:
        query = (
            select(
                orders_table.c.status.label("order_status"),
                func.sum(
                    order_items_table.c.item_quantity
                    * order_items_table.c.price_per_order_item
                ).label("calculated_total_price"),
                order_items_table.c.order_item_title.label("item_title"),
                order_items_table.c.item_quantity.label("item_quantity"),
            )
            .join(
                order_items_table,
                and_(orders_table.c.order_id == order_items_table.c.order_id),
            )
            .where(orders_table.c.order_id == order_id)
            .group_by(
                orders_table.c.status,
                order_items_table.c.order_item_title,
                order_items_table.c.item_quantity,
            )
        )

        result = await self.session.execute(query)
        rows = result.mappings().all()

        items = [
            OrderItemView(
                title=row.item_title,
                quantity=row.item_quantity,
            )
            for row in rows
        ]

        return OrderView(
            status=rows[0].order_status,
            total_price=rows[0].calculated_total_price,
            items=items,
        )
