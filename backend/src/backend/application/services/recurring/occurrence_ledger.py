import logging
from dataclasses import dataclass
from datetime import date

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

logger = logging.getLogger(__name__)


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
        logger.debug(
            "Planning recurring order occurrences: "
            "recurring_order_id=%s dates_count=%d",
            recurring_order_id,
            len(scheduled_dates),
        )
        occurrence_filters = RecurringOrderOccurrenceFilters(
            recurring_order_id=recurring_order_id,
            scheduled_dates=scheduled_dates,
        )
        occurrences = (
            await self._recurring_order_gateway.load_occurrences_by_filters(
                occurrence_filters
            )
        )
        existing_occurrences = {
            occurrence.scheduled_for: occurrence for occurrence in occurrences
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

        plan = RecurringOrderOccurrencePlan(
            dates_to_create=dates_to_create,
            already_scheduled_dates=already_scheduled_dates,
            cancelled_dates=cancelled_dates,
        )
        logger.info(
            "Recurring order occurrence plan built: "
            "recurring_order_id=%s to_create=%d already_scheduled=%d "
            "cancelled=%d",
            recurring_order_id,
            len(plan.dates_to_create),
            len(plan.already_scheduled_dates),
            len(plan.cancelled_dates),
        )
        return plan

    def mark_scheduled(
        self,
        *,
        recurring_order_id: RecurringOrderId,
        scheduled_for: date,
        order_id: OrderId,
    ) -> None:
        logger.debug(
            "Marking recurring order occurrence scheduled: "
            "recurring_order_id=%s scheduled_for=%s order_id=%s",
            recurring_order_id,
            scheduled_for,
            order_id,
        )
        self._recurring_order_gateway.save_occurrence(
            RecurringOrderOccurrence(
                recurring_order_id=recurring_order_id,
                scheduled_for=scheduled_for,
                status=RecurringOrderOccurrenceStatus.SCHEDULED,
                order_id=order_id,
            )
        )
