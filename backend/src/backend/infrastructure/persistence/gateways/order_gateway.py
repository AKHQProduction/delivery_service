from typing import cast
from uuid import UUID

from sqlalchemy import asc, case, desc, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.order_gateway import (
    CategoryStatsReadModel,
    CreateOrderDTO,
    DeliveryAddressDTO,
    GetOrdersFilters,
    Order as OrderEntity,
    OrderGateway,
    OrderItemReadModel,
    OrderReadModel,
    OrderStatsReadModel,
    PaymentMethodStatsReadModel,
    TimeSlotFilter,
    TimeSlotStatsReadModel,
    UpdateOrderDTO,
)
from backend.application.vars import (
    ClientId,
    Empty,
    OrderId,
    PaymentMethod,
    ProductId,
    ShopId,
)
from backend.infrastructure.persistence.tables.categories import Category
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.orders import Order, OrderItem
from backend.infrastructure.persistence.tables.products import Product
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyOrderGateway(OrderGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> OrderId:
        return OrderId(UUID(str(uuid7())))

    async def create_order(self, dto: CreateOrderDTO) -> None:
        delivery_address = {
            "street": dto.delivery_address.street,
            "house": dto.delivery_address.house,
            "apartment": dto.delivery_address.apartment,
            "entrance": dto.delivery_address.entrance,
            "floor": dto.delivery_address.floor,
            "intercom": dto.delivery_address.intercom,
            "comment": dto.delivery_address.comment,
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
            delivery_start_time=dto.delivery_start_time,
            delivery_end_time=dto.delivery_end_time,
            comment=dto.comment,
            shop_id=dto.shop_id,
            client_id=dto.client_id,
            items=order_items,
            payment_method=dto.payment_method,
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
                delivery_start_time=row.delivery_start_time,
                delivery_end_time=row.delivery_end_time,
                delivery_phone=cast("str", cast("object", row.delivery_phone)),
                delivery_address=DeliveryAddressDTO(
                    street=cast("str", delivery_address_dict.get("street")),
                    house=cast("str", delivery_address_dict.get("house")),
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
                    comment=cast(
                        "str | None", delivery_address_dict.get("comment")
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
        if filters.start_date:
            query = query.where(Order.date >= filters.start_date)
        if filters.end_date:
            query = query.where(Order.date <= filters.end_date)
        if filters.delivery_start_time:
            query = query.where(
                Order.delivery_start_time == filters.delivery_start_time
            )

        search_conditions = []
        if filters.client_name:
            query = query.join(Client)
            search_conditions.append(
                Client.full_name.ilike(f"%{escape_like(filters.client_name)}%")
            )
        if search_conditions:
            query = query.where(or_(*search_conditions))

        order_func = desc if pagination.order == SortOrder.DESC else asc
        query = query.order_by(order_func(Order.date), asc(Order.id))
        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [self._to_read_model(row) for row in rows]

    def _to_read_model(self, row: Order) -> OrderReadModel:
        delivery_address_dict = cast(
            "dict[str, object]", cast("object", row.delivery_address)
        )
        time_slot = (
            f"{row.delivery_start_time.strftime('%H:%M')}-"
            f"{row.delivery_end_time.strftime('%H:%M')}"
        )
        return OrderReadModel(
            order_id=OrderId(cast("UUID", cast("object", row.id))),
            date=row.date.strftime("%d.%m.%Y"),
            time_slot=time_slot,
            delivery_phone=cast("str", cast("object", row.delivery_phone)),
            delivery_address=DeliveryAddressDTO(
                street=cast("str", delivery_address_dict.get("street")),
                house=cast("str", delivery_address_dict.get("house")),
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
                comment=cast(
                    "str | None", delivery_address_dict.get("comment")
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
                    price_per_item=int(item.price_per_item),
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
            payment_method=PaymentMethod(
                cast("str", cast("object", row.payment_method))
            ),
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

        if dto.delivery_start_time is not None:
            order_db.delivery_start_time = dto.delivery_start_time

        if dto.delivery_end_time is not None:
            order_db.delivery_end_time = dto.delivery_end_time

        if dto.delivery_phone is not None:
            order_db.delivery_phone = dto.delivery_phone

        if dto.delivery_address is not None:
            order_db.delivery_address = {
                "street": dto.delivery_address.street,
                "house": dto.delivery_address.house,
                "apartment": dto.delivery_address.apartment,
                "entrance": dto.delivery_address.entrance,
                "floor": dto.delivery_address.floor,
                "intercom": dto.delivery_address.intercom,
                "comment": dto.delivery_address.comment,
            }

        if dto.comment is not None:
            if dto.comment == Empty.EMPTY:
                order_db.comment = cast("str", None)
            else:
                order_db.comment = dto.comment

        if dto.payment_method is not None:
            order_db.payment_method = dto.payment_method.value

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
                price_per_item=int(item.price_per_item),
                product_id=(
                    ProductId(cast("UUID", cast("object", item.product_id)))
                    if item.product_id
                    else None
                ),
            )
            for item in items
        ]

    async def get_stats(
        self,
        filters: GetOrdersFilters,
        time_slots_filter: list[TimeSlotFilter],
    ) -> OrderStatsReadModel:
        main_query = (
            select(
                func.count(func.distinct(Order.id)).label("total_orders"),
                func.coalesce(
                    func.sum(OrderItem.quantity * OrderItem.price_per_item), 0
                ).label("total_orders_sum"),
            )
            .select_from(Order)
            .outerjoin(OrderItem, Order.id == OrderItem.order_id)
        )
        main_query = self._apply_order_filters(main_query, filters)

        main_result = await self._session.execute(main_query)
        main_row = main_result.one()

        return OrderStatsReadModel(
            total_orders=main_row.total_orders or 0,
            total_orders_sum=int(main_row.total_orders_sum or 0),
            time_slot_stats=await self._get_time_slot_stats(
                filters, time_slots_filter
            ),
            category_stats=await self._get_category_stats(filters),
            payment_method_stats=await self._get_payment_method_stats(filters),
        )

    async def _get_time_slot_stats(
        self,
        filters: GetOrdersFilters,
        time_slots_filter: list[TimeSlotFilter],
    ) -> list[TimeSlotStatsReadModel]:
        if not time_slots_filter:
            return []

        slot_labels = {
            f"{slot.start_time.strftime('%H:%M')}-"
            f"{slot.end_time.strftime('%H:%M')}": slot
            for slot in time_slots_filter
        }

        time_slot_case = case(
            *[
                (
                    (Order.delivery_start_time >= slot.start_time)
                    & (Order.delivery_start_time < slot.end_time),
                    literal(label),
                )
                for label, slot in slot_labels.items()
            ],
        ).label("time_slot")

        query = (
            select(
                time_slot_case,
                func.count(func.distinct(Order.id)).label("total"),
            )
            .select_from(Order)
            .where(
                or_(*[
                    (Order.delivery_start_time >= slot.start_time)
                    & (Order.delivery_start_time < slot.end_time)
                    for slot in time_slots_filter
                ])
            )
            .group_by(time_slot_case)
        )
        query = self._apply_order_filters(query, filters)

        result = await self._session.execute(query)
        totals_by_slot = {row.time_slot: row.total for row in result.all()}

        return [
            TimeSlotStatsReadModel(
                time_slot=label, total=totals_by_slot.get(label, 0)
            )
            for label in slot_labels
        ]

    async def _get_category_stats(
        self, filters: GetOrdersFilters
    ) -> list[CategoryStatsReadModel]:
        query = (
            select(
                func.coalesce(Category.name, "Без категорії").label(
                    "category_name"
                ),
                func.coalesce(func.sum(OrderItem.quantity), 0).label(
                    "total_quantity"
                ),
            )
            .select_from(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Product, OrderItem.product_id == Product.id)
            .outerjoin(Category, Product.category_id == Category.id)
            .group_by(Category.id, Category.name)
        )
        query = self._apply_order_filters(query, filters)

        result = await self._session.execute(query)
        return [
            CategoryStatsReadModel(
                name=cast("str", row.category_name),
                quantity=int(row.total_quantity or 0),
            )
            for row in result.all()
        ]

    async def _get_payment_method_stats(
        self, filters: GetOrdersFilters
    ) -> list[PaymentMethodStatsReadModel]:
        query = (
            select(
                Order.payment_method.label("payment_method"),
                func.coalesce(
                    func.sum(OrderItem.quantity * OrderItem.price_per_item), 0
                ).label("orders_sum"),
            )
            .select_from(Order)
            .outerjoin(OrderItem, Order.id == OrderItem.order_id)
            .group_by(Order.payment_method)
        )
        query = self._apply_order_filters(query, filters)

        result = await self._session.execute(query)
        return [
            PaymentMethodStatsReadModel(
                method=PaymentMethod(cast("str", row.payment_method)),
                orders_sum=int(row.orders_sum or 0),
            )
            for row in result.all()
        ]

    @staticmethod
    def _apply_order_filters(
        query: Select, filters: GetOrdersFilters
    ) -> Select:
        if filters.shop_id:
            query = query.where(Order.shop_id == filters.shop_id)
        if filters.start_date:
            query = query.where(Order.date >= filters.start_date)
        if filters.end_date:
            query = query.where(Order.date <= filters.end_date)
        return query
