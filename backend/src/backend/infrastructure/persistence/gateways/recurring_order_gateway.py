from datetime import time
from typing import Any
from uuid import UUID

from sqlalchemy import asc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils.compat import uuid7

from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderDetailReadModel,
    RecurringOrderFilters,
    RecurringOrderItemReadModel,
    RecurringOrderReadModel,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    RecurringOrderId,
    ShopId,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.products import Product
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)
from backend.infrastructure.persistence.utils.cast import mapped_cast
from backend.infrastructure.persistence.utils.escape import escape_like


class SQLAlchemyRecurringOrderGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> RecurringOrderId:
        return RecurringOrderId(uuid7())

    def save(self, recurring_order: RecurringOrder) -> None:
        self._session.add(recurring_order)

    async def load(
        self, recurring_order_id: RecurringOrderId
    ) -> RecurringOrder | None:
        return await self._session.get(RecurringOrder, recurring_order_id)

    async def load_with_items(
        self, recurring_order_id: RecurringOrderId
    ) -> RecurringOrder | None:
        query = (
            select(RecurringOrder)
            .where(RecurringOrder.id == recurring_order_id)
            .options(selectinload(RecurringOrder.items))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def load_by_client_refs(
        self,
        client_id: ClientId,
        *,
        phone_ids: set[PhoneId],
        address_ids: set[AddressId],
    ) -> list[RecurringOrder]:
        conditions = []
        if phone_ids:
            conditions.append(RecurringOrder.phone_id.in_(phone_ids))
        if address_ids:
            conditions.append(RecurringOrder.address_id.in_(address_ids))
        if not conditions:
            return []

        query = select(RecurringOrder).where(
            RecurringOrder.client_id == client_id,
            or_(*conditions),
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def delete(self, recurring_order: RecurringOrder) -> None:
        await self._session.delete(recurring_order)

    async def read_all(
        self, shop_id: ShopId, filters: RecurringOrderFilters
    ) -> list[RecurringOrderReadModel]:
        item_count = func.count(RecurringOrderItem.id).label("items_count")
        query = (
            select(
                RecurringOrder,
                Client,
                ClientPhone,
                ClientAddress,
                ShopDeliveryTimeSlot,
                item_count,
            )
            .join(Client, Client.id == RecurringOrder.client_id)
            .outerjoin(ClientPhone, ClientPhone.id == RecurringOrder.phone_id)
            .outerjoin(
                ClientAddress, ClientAddress.id == RecurringOrder.address_id
            )
            .join(
                ShopDeliveryTimeSlot,
                ShopDeliveryTimeSlot.id == RecurringOrder.time_slot_id,
            )
            .outerjoin(
                RecurringOrderItem,
                RecurringOrderItem.recurring_order_id == RecurringOrder.id,
            )
            .where(RecurringOrder.shop_id == shop_id)
            .group_by(
                RecurringOrder.id,
                Client.id,
                ClientPhone.id,
                ClientAddress.id,
                ShopDeliveryTimeSlot.id,
            )
            .order_by(asc(Client.full_name), asc(RecurringOrder.id))
        )
        query = self._apply_filters(query, filters)

        result = await self._session.execute(query)
        return [
            self._to_read_model(
                recurring_order=row[0],
                client=row[1],
                phone=row[2],
                address=row[3],
                time_slot=row[4],
                items_count=int(row[5]),
            )
            for row in result.all()
        ]

    async def read(
        self, recurring_order_id: RecurringOrderId, shop_id: ShopId
    ) -> RecurringOrderDetailReadModel | None:
        item_count = func.count(RecurringOrderItem.id).label("items_count")
        query = (
            select(
                RecurringOrder,
                Client,
                ClientPhone,
                ClientAddress,
                ShopDeliveryTimeSlot,
                item_count,
            )
            .join(Client, Client.id == RecurringOrder.client_id)
            .outerjoin(ClientPhone, ClientPhone.id == RecurringOrder.phone_id)
            .outerjoin(
                ClientAddress, ClientAddress.id == RecurringOrder.address_id
            )
            .join(
                ShopDeliveryTimeSlot,
                ShopDeliveryTimeSlot.id == RecurringOrder.time_slot_id,
            )
            .outerjoin(
                RecurringOrderItem,
                RecurringOrderItem.recurring_order_id == RecurringOrder.id,
            )
            .where(
                RecurringOrder.id == recurring_order_id,
                RecurringOrder.shop_id == shop_id,
            )
            .group_by(
                RecurringOrder.id,
                Client.id,
                ClientPhone.id,
                ClientAddress.id,
                ShopDeliveryTimeSlot.id,
            )
        )
        result = await self._session.execute(query)
        row = result.one_or_none()
        if row is None:
            return None

        items_query = (
            select(RecurringOrderItem, Product)
            .join(Product, Product.id == RecurringOrderItem.product_id)
            .where(RecurringOrderItem.recurring_order_id == recurring_order_id)
            .order_by(asc(Product.name), asc(RecurringOrderItem.id))
        )
        items_result = await self._session.execute(items_query)
        items = [
            RecurringOrderItemReadModel(
                product_id=item.product_id,
                product_name=product.name,
                quantity=item.quantity,
                current_price=int(product.price),
            )
            for item, product in items_result.all()
        ]

        base = self._to_read_model(
            recurring_order=row[0],
            client=row[1],
            phone=row[2],
            address=row[3],
            time_slot=row[4],
            items_count=int(row[5]),
        )
        return RecurringOrderDetailReadModel(
            **base.__dict__,
            payment_method=row[0].payment_method,
            comment=row[0].comment,
            items=items,
        )

    def _apply_filters(
        self, query: Any, filters: RecurringOrderFilters
    ) -> Any:
        if filters.client_name:
            query = query.where(
                Client.full_name.ilike(f"%{escape_like(filters.client_name)}%")
            )
        if filters.status:
            query = query.where(RecurringOrder.status == filters.status)
        if filters.schedule_type:
            query = query.where(
                RecurringOrder.schedule_type == filters.schedule_type
            )
        if filters.weekday is not None:
            query = query.where(
                RecurringOrder.weekdays.contains([filters.weekday])
            )
        if filters.month_day is not None:
            query = query.where(
                RecurringOrder.month_days.contains([filters.month_day])
            )
        return query

    def _to_read_model(
        self,
        *,
        recurring_order: RecurringOrder,
        client: Client,
        phone: ClientPhone | None,
        address: ClientAddress | None,
        time_slot: ShopDeliveryTimeSlot,
        items_count: int,
    ) -> RecurringOrderReadModel:
        return RecurringOrderReadModel(
            recurring_order_id=RecurringOrderId(
                mapped_cast(UUID, recurring_order.id)
            ),
            client_id=ClientId(mapped_cast(UUID, client.id)),
            client_name=mapped_cast(str, client.full_name),
            phone_id=PhoneId(mapped_cast(int, phone.id)) if phone else None,
            phone_number=mapped_cast(str, phone.number) if phone else None,
            address_id=AddressId(mapped_cast(int, address.id))
            if address
            else None,
            address_summary=self._address_summary(address),
            time_slot_id=time_slot.id,
            time_slot_label=time_slot.label,
            delivery_start_time=mapped_cast(
                time, time_slot.start_time
            ).strftime("%H:%M"),
            delivery_end_time=mapped_cast(time, time_slot.end_time).strftime(
                "%H:%M"
            ),
            schedule_type=recurring_order.schedule_type,
            weekdays=recurring_order.weekdays,
            month_days=recurring_order.month_days,
            items_count=items_count,
            status=recurring_order.status,
        )

    def _address_summary(self, address: ClientAddress | None) -> str | None:
        if address is None:
            return None

        parts = [
            address.street,
            address.house,
            f"кв. {address.apartment}" if address.apartment else None,
        ]
        return ", ".join(part for part in parts if part)
