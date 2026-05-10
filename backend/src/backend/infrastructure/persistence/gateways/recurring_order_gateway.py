from dataclasses import dataclass
from datetime import date

from sqlalchemy import Select, asc, delete, or_, select
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
    RecurringOrderStatus,
    TimeSlotId,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
    RecurringOrderOccurrence,
)


@dataclass(frozen=True)
class RecurringOrderFilters:
    status: RecurringOrderStatus | None = None
    client_id: ClientId | None = None
    phone_ids: set[PhoneId] | None = None
    address_ids: set[AddressId] | None = None
    product_id: ProductId | None = None
    time_slot_id: TimeSlotId | None = None
    with_items: bool = False


@dataclass(frozen=True)
class RecurringOrderOccurrenceFilters:
    recurring_order_id: RecurringOrderId | None = None
    scheduled_dates: list[date] | None = None
    from_date: date | None = None
    order_id: OrderId | None = None
    with_order: bool | None = None


class SQLAlchemyRecurringOrderGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> RecurringOrderId:
        return RecurringOrderId(uuid7())

    def save(self, recurring_order: RecurringOrder) -> None:
        self._session.add(recurring_order)

    def save_occurrence(self, occurrence: RecurringOrderOccurrence) -> None:
        self._session.add(occurrence)

    async def delete_occurrence(
        self, occurrence: RecurringOrderOccurrence
    ) -> None:
        await self._session.delete(occurrence)

    async def delete_occurrences_from(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
    ) -> None:
        await self._session.execute(
            delete(RecurringOrderOccurrence).where(
                RecurringOrderOccurrence.recurring_order_id
                == recurring_order_id,
                RecurringOrderOccurrence.scheduled_for >= from_date,
            )
        )

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

    async def load_by_filters(
        self, filters: RecurringOrderFilters
    ) -> list[RecurringOrder]:
        query = select(RecurringOrder)
        if filters.product_id is not None:
            query = query.join(RecurringOrderItem)
        if filters.with_items:
            query = query.options(selectinload(RecurringOrder.items))

        conditions = []
        if filters.status is not None:
            conditions.append(RecurringOrder.status == filters.status)
        if filters.client_id is not None:
            conditions.append(RecurringOrder.client_id == filters.client_id)
        if filters.phone_ids:
            conditions.append(RecurringOrder.phone_id.in_(filters.phone_ids))
        if filters.address_ids:
            conditions.append(
                RecurringOrder.address_id.in_(filters.address_ids)
            )
        if filters.product_id is not None:
            conditions.append(
                RecurringOrderItem.product_id == filters.product_id
            )
        if filters.time_slot_id is not None:
            conditions.append(
                RecurringOrder.time_slot_id == filters.time_slot_id
            )

        if (
            filters.client_id is not None
            and filters.phone_ids is not None
            and filters.address_ids is not None
            and not filters.phone_ids
            and not filters.address_ids
        ):
            return []

        if filters.client_id is not None and (
            filters.phone_ids or filters.address_ids
        ):
            reference_conditions = []
            if filters.phone_ids:
                reference_conditions.append(
                    RecurringOrder.phone_id.in_(filters.phone_ids)
                )
            if filters.address_ids:
                reference_conditions.append(
                    RecurringOrder.address_id.in_(filters.address_ids)
                )
            query = query.where(
                RecurringOrder.client_id == filters.client_id,
                or_(*reference_conditions),
            )
        elif conditions:
            query = query.where(*conditions)

        query = query.order_by(asc(RecurringOrder.id))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def load_occurrence_by_filters(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> RecurringOrderOccurrence | None:
        query = self._build_occurrence_query(filters)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def load_occurrences_by_filters(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> list[RecurringOrderOccurrence]:
        if filters.scheduled_dates == []:
            return []
        query = self._build_occurrence_query(filters).order_by(
            asc(RecurringOrderOccurrence.scheduled_for)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def delete(self, recurring_order: RecurringOrder) -> None:
        await self._session.delete(recurring_order)

    def _build_occurrence_query(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> Select[tuple[RecurringOrderOccurrence]]:
        query = select(RecurringOrderOccurrence)
        conditions = []
        if filters.recurring_order_id is not None:
            conditions.append(
                RecurringOrderOccurrence.recurring_order_id
                == filters.recurring_order_id
            )
        if filters.scheduled_dates is not None:
            conditions.append(
                RecurringOrderOccurrence.scheduled_for.in_(
                    filters.scheduled_dates
                )
            )
        if filters.from_date is not None:
            conditions.append(
                RecurringOrderOccurrence.scheduled_for >= filters.from_date
            )
        if filters.order_id is not None:
            conditions.append(
                RecurringOrderOccurrence.order_id == filters.order_id
            )
        if filters.with_order is True:
            conditions.append(RecurringOrderOccurrence.order_id.is_not(None))
        if filters.with_order is False:
            conditions.append(RecurringOrderOccurrence.order_id.is_(None))
        if conditions:
            query = query.where(*conditions)
        return query
