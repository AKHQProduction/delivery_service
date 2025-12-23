from typing import cast
from uuid import UUID

from sqlalchemy import asc, case, func, or_, select
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
    OrderStatsReadModel,
    UpdateOrderDTO,
)
from backend.application.vars import (
    AddressType,
    ClientId,
    Empty,
    OrderId,
    ProductId,
    ShopId,
    TimePreference,
)
from backend.infrastructure.persistence.tables.clients import Client
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
                product_id=item.product_id,
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

        search_conditions = []
        if filters.client_name:
            query = query.join(Client)
            search_conditions.append(
                Client.full_name.ilike(f"%{filters.client_name}%")
            )
        if filters.custom_id:
            if not filters.client_name:
                query = query.join(Client)
            search_conditions.append(
                Client.custom_id.ilike(f"%{filters.custom_id}%")
            )

        if search_conditions:
            query = query.where(or_(*search_conditions))

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
                    product_id=(
                        ProductId(
                            cast("UUID", cast("object", item.product_id))
                        )
                        if item.product_id
                        else None
                    ),
                )
                for item in row.items
            ],
        )

    async def update(self, dto: UpdateOrderDTO) -> None:
        query = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == dto.order_id)
        )
        result = await self._session.execute(query)
        order_db = result.scalar_one_or_none()

        if not order_db:
            return

        if dto.client_id is not None:
            order_db.client_id = dto.client_id

        if dto.delivery_date is not None:
            order_db.date = dto.delivery_date

        if dto.time_preference is not None:
            order_db.time_preference = dto.time_preference.value

        if dto.delivery_phone is not None:
            order_db.delivery_phone = dto.delivery_phone

        if dto.delivery_address is not None:
            order_db.delivery_address = {
                "street": dto.delivery_address.street,
                "house": dto.delivery_address.house,
                "address_type": dto.delivery_address.address_type.value,
                "apartment": dto.delivery_address.apartment,
                "entrance": dto.delivery_address.entrance,
                "floor": dto.delivery_address.floor,
                "intercom": dto.delivery_address.intercom,
            }

        if dto.comment is not None:
            if dto.comment == Empty.EMPTY:
                order_db.comment = cast("str", None)
            else:
                order_db.comment = dto.comment

        # Process items - full replacement
        if dto.items is not None:
            existing_items_map = {item.id: item for item in order_db.items}
            new_ids = {item.id for item in dto.items if item.id is not None}

            # Delete items not in new list
            for item in order_db.items:
                if item.id not in new_ids:
                    await self._session.delete(item)

            # Update existing or add new items
            for item_dto in dto.items:
                if (
                    item_dto.id is not None
                    and item_dto.id in existing_items_map
                ):
                    # Update existing item (partial update supported)
                    item = existing_items_map[item_dto.id]
                    item.quantity = item_dto.quantity
                    if item_dto.name is not None:
                        item.name = item_dto.name
                    if item_dto.price_per_item is not None:
                        item.price_per_item = item_dto.price_per_item
                    if item_dto.product_id is not None:
                        item.product_id = item_dto.product_id
                else:
                    # Add new item
                    new_item = OrderItem(
                        name=item_dto.name or "",
                        quantity=item_dto.quantity,
                        price_per_item=item_dto.price_per_item or 0,
                        order_id=dto.order_id,
                        product_id=item_dto.product_id,
                    )
                    self._session.add(new_item)

    async def load_items(self, order_id: OrderId) -> list[OrderItemReadModel]:
        query = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self._session.execute(query)
        items = result.scalars().all()

        return [
            OrderItemReadModel(
                id=int(cast("int", cast("object", item.id))),
                name=cast("str", cast("object", item.name)),
                quantity=int(cast("int", cast("object", item.quantity))),
                price_per_item=int(
                    cast("int", cast("object", item.price_per_item))
                ),
                product_id=(
                    ProductId(cast("UUID", cast("object", item.product_id)))
                    if item.product_id
                    else None
                ),
            )
            for item in items
        ]

    async def get_stats(
        self, filters: GetOrdersFilters
    ) -> OrderStatsReadModel:
        query = (
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(
                    case(
                        (
                            Order.time_preference
                            == TimePreference.FIRST_HALF.value,
                            1,
                        ),
                        else_=0,
                    )
                ).label("total_orders_in_first_half"),
                func.sum(
                    case(
                        (
                            Order.time_preference
                            == TimePreference.SECOND_HALF.value,
                            1,
                        ),
                        else_=0,
                    )
                ).label("total_orders_in_second_half"),
                func.coalesce(
                    func.sum(OrderItem.quantity * OrderItem.price_per_item), 0
                ).label("total_orders_sum"),
            )
            .select_from(Order)
            .outerjoin(OrderItem, Order.id == OrderItem.order_id)
        )

        if filters.shop_id:
            query = query.where(Order.shop_id == filters.shop_id)
        if filters.delivery_date:
            query = query.where(Order.date == filters.delivery_date)

        result = await self._session.execute(query)
        row = result.one()

        return OrderStatsReadModel(
            total_orders=row.total_orders or 0,
            total_orders_in_first_half=int(
                row.total_orders_in_first_half or 0
            ),
            total_orders_in_second_half=int(
                row.total_orders_in_second_half or 0
            ),
            total_orders_sum=int(row.total_orders_sum or 0),
        )
