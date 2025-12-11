from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    OrderGateway,
)
from backend.application.vars import OrderId
from backend.infrastructure.persistence.tables.orders import Order, OrderItem


class SQLAlchemyOrderGateway(OrderGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> OrderId:
        return OrderId(UUID(str(uuid7())))

    async def create_order(self, dto: CreateOrderDTO) -> None:
        delivery_address = {
            "street": dto.delivery_address.street,
            "house": dto.delivery_address.house,
            "address_type": dto.delivery_address.address_type.value,
            "apartment": dto.delivery_address.apartment,
            "entrance": dto.delivery_address.entrance,
            "floor": dto.delivery_address.floor,
            "intercom": dto.delivery_address.intercom,
        }

        order_items = [
            OrderItem(
                name=item.name,
                quantity=item.quantity,
                price_per_item=item.price_per_item,
            )
            for item in dto.order_items
        ]

        new_order = Order(
            id=dto.order_id,
            date=dto.delivery_date,
            delivery_address=delivery_address,
            delivery_phone=dto.delivery_phone,
            time_preference=dto.time_preference.value,
            comment=dto.comment,
            shop_id=dto.shop_id,
            client_id=dto.client_id,
            items=order_items,
        )

        self._session.add(new_order)
