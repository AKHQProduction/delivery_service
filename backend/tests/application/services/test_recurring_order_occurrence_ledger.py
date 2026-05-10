from datetime import date
from typing import cast
from uuid import UUID

import pytest

from backend.application.services.recurring_order_occurrence_ledger import (
    RecurringOrderOccurrenceLedger,
)
from backend.application.vars import (
    OrderId,
    RecurringOrderId,
    RecurringOrderOccurrenceStatus,
)
from backend.infrastructure.persistence.gateways import (
    RecurringOrderOccurrenceFilters,
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrderOccurrence,
)


class FakeRecurringOrderGateway:
    def __init__(
        self,
        occurrences: list[RecurringOrderOccurrence] | None = None,
    ) -> None:
        self.occurrences = occurrences or []
        self.saved_occurrences: list[RecurringOrderOccurrence] = []

    async def load_occurrences_by_filters(
        self, filters: RecurringOrderOccurrenceFilters
    ) -> list[RecurringOrderOccurrence]:
        return [
            occurrence
            for occurrence in self.occurrences
            if occurrence.recurring_order_id == filters.recurring_order_id
            and occurrence.scheduled_for in (filters.scheduled_dates or [])
        ]

    def save_occurrence(self, occurrence: RecurringOrderOccurrence) -> None:
        self.saved_occurrences.append(occurrence)


@pytest.mark.asyncio()
async def test_plan_dates_splits_new_scheduled_and_cancelled_dates() -> None:
    recurring_order_id = RecurringOrderId(
        UUID("11111111-1111-1111-1111-111111111111")
    )
    scheduled_order_id = OrderId(UUID("22222222-2222-2222-2222-222222222222"))
    ledger = RecurringOrderOccurrenceLedger(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            FakeRecurringOrderGateway([
                RecurringOrderOccurrence(
                    recurring_order_id=recurring_order_id,
                    scheduled_for=date(2026, 5, 11),
                    status=RecurringOrderOccurrenceStatus.SCHEDULED,
                    order_id=scheduled_order_id,
                ),
                RecurringOrderOccurrence(
                    recurring_order_id=recurring_order_id,
                    scheduled_for=date(2026, 5, 13),
                    status=RecurringOrderOccurrenceStatus.CANCELLED,
                    order_id=None,
                ),
            ]),
        )
    )

    plan = await ledger.plan_dates(
        recurring_order_id,
        [
            date(2026, 5, 11),
            date(2026, 5, 13),
            date(2026, 5, 15),
        ],
    )

    assert plan.dates_to_create == [date(2026, 5, 15)]
    assert plan.already_scheduled_dates == [date(2026, 5, 11)]
    assert plan.cancelled_dates == [date(2026, 5, 13)]


def test_mark_scheduled_saves_scheduled_occurrence() -> None:
    recurring_order_id = RecurringOrderId(
        UUID("11111111-1111-1111-1111-111111111111")
    )
    order_id = OrderId(UUID("22222222-2222-2222-2222-222222222222"))
    gateway = FakeRecurringOrderGateway()
    ledger = RecurringOrderOccurrenceLedger(
        cast("SQLAlchemyRecurringOrderGateway", gateway)
    )

    ledger.mark_scheduled(
        recurring_order_id=recurring_order_id,
        scheduled_for=date(2026, 5, 11),
        order_id=order_id,
    )

    assert len(gateway.saved_occurrences) == 1
    occurrence = gateway.saved_occurrences[0]
    assert occurrence.recurring_order_id == recurring_order_id
    assert occurrence.scheduled_for == date(2026, 5, 11)
    assert occurrence.status == RecurringOrderOccurrenceStatus.SCHEDULED
    assert occurrence.order_id == order_id
