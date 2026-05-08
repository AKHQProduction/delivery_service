from dataclasses import dataclass
from datetime import date

from backend.application.vars import (
    OrderId,
    RecurringOrderId,
    RecurringOrderOccurrenceStatus,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrderOccurrence,
)


@dataclass(frozen=True)
class RecurringOrderOccurrencePlan:
    dates_to_create: list[date]
    already_scheduled_dates: list[date]
    cancelled_dates: list[date]


class RecurringOrderOccurrenceLedger:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway

    async def plan_dates(
        self,
        recurring_order_id: RecurringOrderId,
        scheduled_dates: list[date],
    ) -> RecurringOrderOccurrencePlan:
        existing_occurrences = {
            occurrence.scheduled_for: occurrence
            for occurrence in (
                await self._recurring_order_gateway.load_occurrences_for_dates(
                    recurring_order_id, scheduled_dates
                )
            )
        }

        dates_to_create: list[date] = []
        already_scheduled_dates: list[date] = []
        cancelled_dates: list[date] = []
        for scheduled_for in scheduled_dates:
            existing = existing_occurrences.get(scheduled_for)
            if existing is None:
                dates_to_create.append(scheduled_for)
                continue
            if existing.status == RecurringOrderOccurrenceStatus.CANCELLED:
                cancelled_dates.append(scheduled_for)
                continue
            already_scheduled_dates.append(scheduled_for)

        return RecurringOrderOccurrencePlan(
            dates_to_create=dates_to_create,
            already_scheduled_dates=already_scheduled_dates,
            cancelled_dates=cancelled_dates,
        )

    def mark_scheduled(
        self,
        *,
        recurring_order_id: RecurringOrderId,
        scheduled_for: date,
        order_id: OrderId,
    ) -> None:
        self._recurring_order_gateway.save_occurrence(
            RecurringOrderOccurrence(
                recurring_order_id=recurring_order_id,
                scheduled_for=scheduled_for,
                status=RecurringOrderOccurrenceStatus.SCHEDULED,
                order_id=order_id,
            )
        )
