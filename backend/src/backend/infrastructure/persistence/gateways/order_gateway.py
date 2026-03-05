import datetime
import json
from uuid import UUID

from sqlalchemy import asc, case, desc, func, literal, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from uuid_utils.compat import uuid7

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways import Pagination, SortOrder
from backend.application.dto.gateways.order_gateway import (
    CategoryStatsReadModel,
    GetOrdersFilters,
    OrderItemReadModel,
    OrderReadModel,
    OrderStatsReadModel,
    PaymentMethodStatsReadModel,
    TimeSlotFilter,
    TimeSlotStatsReadModel,
)
from backend.application.validators import (
    HOUSE_LETTER_SQL_RE,
    HOUSE_LETTER_SQL_REPL,
    STREET_PREFIX_SQL_RE,
    normalize_house,
    normalize_street,
)
from backend.application.vars import (
    ClientId,
    OrderId,
    PaymentMethod,
    ProductId,
    ShopId,
)
from backend.infrastructure.persistence.tables.categories import Category
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.orders import (
    Order,
    OrderItem,
)
from backend.infrastructure.persistence.tables.products import Product
from backend.infrastructure.persistence.utils.cast import mapped_cast
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyOrderGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> OrderId:
        return OrderId(uuid7())

    def save(self, order: Order) -> None:
        self._session.add(order)

    async def load(self, order_id: OrderId) -> Order | None:
        return await self._session.get(Order, order_id)

    async def load_with_items(self, order_id: OrderId) -> Order | None:
        query = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, order: Order) -> None:
        await self._session.delete(order)

    async def delete_items(self, items: list[OrderItem]) -> None:
        for item in items:
            await self._session.delete(item)

    async def read(
        self, order_id: OrderId, shop_id: ShopId
    ) -> OrderReadModel | None:
        query = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.client),
            )
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
            selectinload(Order.items),
            selectinload(Order.client),
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
        time_slot = (
            f"{row.delivery_start_time.strftime('%H:%M')}-"
            f"{row.delivery_end_time.strftime('%H:%M')}"
        )
        return OrderReadModel(
            order_id=OrderId(mapped_cast(UUID, row.id)),
            date=row.date.strftime("%d.%m.%Y"),
            time_slot=time_slot,
            delivery_phone=mapped_cast(str, row.delivery_phone),
            delivery_address=row.delivery_address,
            comment=mapped_cast(str, row.comment),
            client_id=ClientId(mapped_cast(UUID, row.client_id)),
            client_name=mapped_cast(str, row.client.full_name),
            items=[self._to_item_read_model(item) for item in row.items],
            payment_method=PaymentMethod(mapped_cast(str, row.payment_method)),
        )

    @staticmethod
    def _to_item_read_model(item: OrderItem) -> OrderItemReadModel:
        return OrderItemReadModel(
            id=mapped_cast(int, item.id),
            name=mapped_cast(str, item.name),
            quantity=mapped_cast(int, item.quantity),
            price_per_item=int(item.price_per_item),
            product_id=(
                ProductId(mapped_cast(UUID, item.product_id))
                if item.product_id
                else None
            ),
        )

    async def load_by_date(
        self,
        shop_id: ShopId,
        delivery_date: datetime.date,
        start_time: datetime.time | None = None,
        end_time: datetime.time | None = None,
    ) -> list[Order]:
        query = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.client),
            )
            .where(
                Order.shop_id == shop_id,
                Order.date == delivery_date,
            )
            .order_by(asc(Order.delivery_start_time), asc(Order.id))
        )

        if start_time is not None and end_time is not None:
            query = query.where(
                Order.delivery_start_time == start_time,
                Order.delivery_end_time == end_time,
            )

        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def load_items(self, order_id: OrderId) -> list[OrderItemReadModel]:
        query = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self._session.execute(query)
        items = result.scalars().all()

        return [self._to_item_read_model(item) for item in items]

    async def get_stats(
        self,
        filters: GetOrdersFilters,
        time_slots_filter: list[TimeSlotFilter],
    ) -> OrderStatsReadModel:
        payment_method_stats = await self._get_payment_method_stats(filters)

        total_orders_sum = sum(pm.orders_sum for pm in payment_method_stats)

        total_orders_query = select(
            func.count(Order.id).label("total_orders"),
        ).select_from(Order)
        total_orders_query = self._apply_order_filters(
            total_orders_query, filters
        )
        total_orders_result = await self._session.execute(total_orders_query)
        total_orders = total_orders_result.scalar_one() or 0

        return OrderStatsReadModel(
            total_orders=total_orders,
            total_orders_sum=int(total_orders_sum),
            time_slot_stats=await self._get_time_slot_stats(
                filters, time_slots_filter
            ),
            category_stats=await self._get_category_stats(filters),
            payment_method_stats=payment_method_stats,
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
                time_slot=label,
                total=totals_by_slot.get(label, 0),
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
                name=mapped_cast(str, row.category_name),
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
                    func.sum(OrderItem.quantity * OrderItem.price_per_item),
                    0,
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
                method=PaymentMethod(mapped_cast(str, row.payment_method)),
                orders_sum=int(row.orders_sum or 0),
            )
            for row in result.all()
        ]

    async def update_delivery_coordinates(
        self,
        shop_id: ShopId,
        client_id: ClientId,
        street: str,
        house: str,
        new_coordinates: CoordinatesDTO,
        from_date: datetime.date,
    ) -> int:
        stmt = text("""
            UPDATE orders
            SET delivery_address = jsonb_set(
                delivery_address,
                '{coordinates}',
                CAST(:coords AS jsonb)
            ),
            updated_at = now()
            WHERE shop_id = :shop_id
              AND client_id = :client_id
              AND btrim(regexp_replace(
                    lower(btrim(delivery_address->>'street')),
                    :street_re, ''
                  )) = :street
              AND regexp_replace(
                    lower(btrim(delivery_address->>'house')),
                    :house_re, :house_repl, 'g'
                  ) = :house
              AND date >= :from_date
        """)
        result = await self._session.execute(
            stmt,
            {
                "coords": json.dumps({
                    "latitude": new_coordinates.latitude,
                    "longitude": new_coordinates.longitude,
                }),
                "shop_id": str(shop_id),
                "client_id": str(client_id),
                "street": normalize_street(street),
                "house": normalize_house(house),
                "street_re": STREET_PREFIX_SQL_RE,
                "house_re": HOUSE_LETTER_SQL_RE,
                "house_repl": HOUSE_LETTER_SQL_REPL,
                "from_date": from_date,
            },
        )
        return result.rowcount  # type: ignore[attr-defined]

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
