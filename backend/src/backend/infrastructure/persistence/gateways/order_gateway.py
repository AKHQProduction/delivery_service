from typing import cast
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    GetOrdersFilters,
    Order as OrderEntity,
    OrderGateway,
    OrderItemReadModel,
    OrderReadModel,
)
from backend.application.vars import (
    AddressType,
    ClientId,
    OrderId,
    ShopId,
    TimePreference,
)
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

    async def load(self, order_id: OrderId) -> OrderEntity | None:
        row = await self._session.get(Order, order_id)
        if row:
            delivery_address_dict = cast(
                "dict[str, object]", cast("object", row.delivery_address)
            )
            return OrderEntity(
                order_id=OrderId(cast("UUID", cast("object", row.id))),
                shop_id=ShopId(cast("UUID", cast("object", row.shop_id))),
                client_id=ClientId(
                    cast("UUID", cast("object", row.client_id))
                ),
                delivery_date=row.date,
                time_preference=TimePreference(
                    cast("str", cast("object", row.time_preference))
                ),
                delivery_phone=cast("str", cast("object", row.delivery_phone)),
                delivery_address=DeliveryAddressDTO(
                    street=cast("str", delivery_address_dict.get("street")),
                    house=cast("str", delivery_address_dict.get("house")),
                    address_type=AddressType(
                        cast("str", delivery_address_dict.get("address_type"))
                    ),
                    apartment=cast(
                        "str | None", delivery_address_dict.get("apartment")
                    ),
                    entrance=cast(
                        "str | None", delivery_address_dict.get("entrance")
                    ),
                    floor=cast(
                        "str | None", delivery_address_dict.get("floor")
                    ),
                    intercom=cast(
                        "str | None", delivery_address_dict.get("intercom")
                    ),
                ),
                comment=cast("str | None", cast("object", row.comment)),
            )
        return None

    async def delete(self, order_id: OrderId) -> None:
        order_db = await self._session.get(Order, order_id)
        if order_db:
            await self._session.delete(order_db)

    async def read(
        self, order_id: OrderId, shop_id: ShopId
    ) -> OrderReadModel | None:
        query = (
            select(Order)
            .options(selectinload(Order.items), selectinload(Order.client))
            .where(Order.id == order_id, Order.shop_id == shop_id)
        )
        result = await self._session.execute(query)
        row = result.scalar_one_or_none()

        if row:
            return self._to_read_model(row)
        return None

    async def read_all(
        self, filters: GetOrdersFilters, pagination: Pagination
    ) -> list[OrderReadModel]:
        query = select(Order).options(
            selectinload(Order.items), selectinload(Order.client)
        )

        if filters.shop_id:
            query = query.where(Order.shop_id == filters.shop_id)
        if filters.delivery_date:
            query = query.where(Order.date == filters.delivery_date)
        if filters.time_preference:
            query = query.where(
                Order.time_preference == filters.time_preference.value
            )

        query = query.order_by(asc(Order.date))
        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [self._to_read_model(row) for row in rows]

    def _to_read_model(self, row: Order) -> OrderReadModel:
        delivery_address_dict = cast(
            "dict[str, object]", cast("object", row.delivery_address)
        )
        return OrderReadModel(
            order_id=OrderId(cast("UUID", cast("object", row.id))),
            date=row.date,
            time_preference=TimePreference(
                cast("str", cast("object", row.time_preference))
            ),
            delivery_phone=cast("str", cast("object", row.delivery_phone)),
            delivery_address=DeliveryAddressDTO(
                street=cast("str", delivery_address_dict.get("street")),
                house=cast("str", delivery_address_dict.get("house")),
                address_type=AddressType(
                    cast("str", delivery_address_dict.get("address_type"))
                ),
                apartment=cast(
                    "str | None", delivery_address_dict.get("apartment")
                ),
                entrance=cast(
                    "str | None", delivery_address_dict.get("entrance")
                ),
                floor=cast("str | None", delivery_address_dict.get("floor")),
                intercom=cast(
                    "str | None", delivery_address_dict.get("intercom")
                ),
            ),
            comment=cast("str | None", cast("object", row.comment)),
            client_id=ClientId(cast("UUID", cast("object", row.client_id))),
            client_name=cast("str", cast("object", row.client.full_name)),
            items=[
                OrderItemReadModel(
                    id=int(cast("int", cast("object", item.id))),
                    name=cast("str", cast("object", item.name)),
                    quantity=int(cast("int", cast("object", item.quantity))),
                    price_per_item=int(
                        cast("int", cast("object", item.price_per_item))
                    ),
                )
                for item in row.items
            ],
        )
