from datetime import date

from sqlalchemy import asc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid_utils.compat import uuid7

from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PhoneId,
    ProductId,
    RecurringOrderId,
    TimeSlotId,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
    RecurringOrderOccurrence,
)


class SQLAlchemyRecurringOrderGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> RecurringOrderId:
        return RecurringOrderId(uuid7())

    def save(self, recurring_order: RecurringOrder) -> None:
        self._session.add(recurring_order)

    def save_occurrence(self, occurrence: RecurringOrderOccurrence) -> None:
        self._session.add(occurrence)

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

    async def load_occurrences_for_dates(
        self,
        recurring_order_id: RecurringOrderId,
        dates: list[date],
    ) -> list[RecurringOrderOccurrence]:
        if not dates:
            return []

        query = select(RecurringOrderOccurrence).where(
            RecurringOrderOccurrence.recurring_order_id == recurring_order_id,
            RecurringOrderOccurrence.scheduled_for.in_(dates),
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def load_occurrence_by_order(
        self, order_id: OrderId
    ) -> RecurringOrderOccurrence | None:
        query = select(RecurringOrderOccurrence).where(
            RecurringOrderOccurrence.order_id == order_id
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def load_scheduled_occurrences_from(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
    ) -> list[RecurringOrderOccurrence]:
        query = (
            select(RecurringOrderOccurrence)
            .where(
                RecurringOrderOccurrence.recurring_order_id
                == recurring_order_id,
                RecurringOrderOccurrence.scheduled_for >= from_date,
                RecurringOrderOccurrence.order_id.is_not(None),
            )
            .order_by(asc(RecurringOrderOccurrence.scheduled_for))
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

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

    async def load_by_product(
        self, product_id: ProductId
    ) -> list[RecurringOrder]:
        query = (
            select(RecurringOrder)
            .join(RecurringOrderItem)
            .where(RecurringOrderItem.product_id == product_id)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def load_by_time_slot(
        self, time_slot_id: TimeSlotId
    ) -> list[RecurringOrder]:
        query = select(RecurringOrder).where(
            RecurringOrder.time_slot_id == time_slot_id
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def delete(self, recurring_order: RecurringOrder) -> None:
        await self._session.delete(recurring_order)
