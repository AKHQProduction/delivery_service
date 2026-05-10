from datetime import date
from typing import cast
from uuid import UUID

import pytest

from backend.application.dto.idp import CurrentUserDTO
from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.services.order_deletion import OrderDeletion
from backend.application.vars import (
    ClientId,
    OrderId,
    RecurringOrderId,
    RecurringOrderOccurrenceStatus,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    ShopRole,
    TimeSlotId,
    UserId,
)
from backend.infrastructure.persistence.gateways import (
    RecurringOrderOccurrenceFilters,
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderOccurrence,
)

SHOP_ID = ShopId(UUID("11111111-1111-1111-1111-111111111111"))
CLIENT_ID = ClientId(UUID("22222222-2222-2222-2222-222222222222"))
TIME_SLOT_ID = TimeSlotId(UUID("33333333-3333-3333-3333-333333333333"))
RECURRING_ORDER_ID = RecurringOrderId(
    UUID("44444444-4444-4444-4444-444444444444")
)
ORDER_ID = OrderId(UUID("55555555-5555-5555-5555-555555555555"))


class FakeRecurringOrderGateway:
    def __init__(
        self,
        recurring_order: RecurringOrder,
        occurrences: list[RecurringOrderOccurrence],
    ) -> None:
        self.recurring_order = recurring_order
        self.occurrences = occurrences

    async def load_occurrence_by_filters(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> RecurringOrderOccurrence | None:
        for occurrence in self.occurrences:
            if occurrence.order_id == filters.order_id:
                return occurrence
        return None

    async def load_occurrences_by_filters(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> list[RecurringOrderOccurrence]:
        occurrences = self.occurrences
        if filters.recurring_order_id is not None:
            occurrences = [
                occurrence
                for occurrence in occurrences
                if occurrence.recurring_order_id == filters.recurring_order_id
            ]
        if filters.from_date is not None:
            occurrences = [
                occurrence
                for occurrence in occurrences
                if occurrence.scheduled_for >= filters.from_date
            ]
        if filters.with_order is True:
            occurrences = [
                occurrence
                for occurrence in occurrences
                if occurrence.order_id is not None
            ]
        return occurrences

    async def load(
        self, recurring_order_id: RecurringOrderId
    ) -> RecurringOrder | None:
        if self.recurring_order.id == recurring_order_id:
            return self.recurring_order
        return None


class FakeOrderDeletion:
    def __init__(self) -> None:
        self.deleted_order_ids: list[OrderId] = []

    async def delete(
        self, order_id: OrderId, current_user: CurrentUserDTO
    ) -> None:
        self.deleted_order_ids.append(order_id)


def _current_user() -> CurrentUserDTO:
    return CurrentUserDTO(
        user_id=UserId(UUID("66666666-6666-6666-6666-666666666666")),
        full_name="Manager",
        role=ShopRole.MANAGER,
        shop_id=SHOP_ID,
    )


def _recurring_order() -> RecurringOrder:
    return RecurringOrder(
        id=RECURRING_ORDER_ID,
        shop_id=SHOP_ID,
        client_id=CLIENT_ID,
        address_id=None,
        phone_id=None,
        time_slot_id=TIME_SLOT_ID,
        payment_method="Готівка",
        comment=None,
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        status=RecurringOrderStatus.ACTIVE,
    )


@pytest.mark.asyncio()
async def test_delete_generated_order_cancels_occurrence_and_pauses() -> None:
    recurring_order = _recurring_order()
    occurrence = RecurringOrderOccurrence(
        recurring_order_id=RECURRING_ORDER_ID,
        scheduled_for=date(2026, 5, 11),
        status=RecurringOrderOccurrenceStatus.SCHEDULED,
        order_id=ORDER_ID,
    )
    order_deletion = FakeOrderDeletion()
    lifecycle = GeneratedOrderLifecycle(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            FakeRecurringOrderGateway(recurring_order, [occurrence]),
        ),
        cast("OrderDeletion", order_deletion),
    )

    await lifecycle.delete_order(
        ORDER_ID,
        _current_user(),
        pause_recurring_order=True,
    )

    assert occurrence.status == RecurringOrderOccurrenceStatus.CANCELLED
    assert occurrence.order_id is None
    assert recurring_order.status == RecurringOrderStatus.PAUSED
    assert order_deletion.deleted_order_ids == [ORDER_ID]


@pytest.mark.asyncio()
async def test_delete_future_orders_cancels_matching_orders() -> None:
    recurring_order = _recurring_order()
    today_occurrence = RecurringOrderOccurrence(
        recurring_order_id=RECURRING_ORDER_ID,
        scheduled_for=date(2026, 5, 8),
        status=RecurringOrderOccurrenceStatus.SCHEDULED,
        order_id=OrderId(UUID("77777777-7777-7777-7777-777777777777")),
    )
    future_occurrence = RecurringOrderOccurrence(
        recurring_order_id=RECURRING_ORDER_ID,
        scheduled_for=date(2026, 5, 11),
        status=RecurringOrderOccurrenceStatus.SCHEDULED,
        order_id=ORDER_ID,
    )
    order_deletion = FakeOrderDeletion()
    lifecycle = GeneratedOrderLifecycle(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            FakeRecurringOrderGateway(
                recurring_order, [today_occurrence, future_occurrence]
            ),
        ),
        cast("OrderDeletion", order_deletion),
    )

    await lifecycle.delete_future_orders(
        RECURRING_ORDER_ID,
        date(2026, 5, 9),
        _current_user(),
    )

    assert today_occurrence.status == RecurringOrderOccurrenceStatus.SCHEDULED
    assert today_occurrence.order_id is not None
    assert future_occurrence.status == RecurringOrderOccurrenceStatus.CANCELLED
    assert future_occurrence.order_id is None
    assert order_deletion.deleted_order_ids == [ORDER_ID]
