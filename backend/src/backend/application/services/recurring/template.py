from backend.application.errors import (
    InvalidRecurringOrderScheduleError,
    RecurringOrderHasNoItemsError,
    RecurringOrderItemQuantityError,
)
from backend.application.vars import ScheduleType


def normalize_schedule(
    *,
    schedule_type: ScheduleType,
    weekdays: list[int] | None,
    month_days: list[int] | None,
) -> tuple[list[int] | None, list[int] | None]:
    if schedule_type == ScheduleType.WEEKLY:
        if not weekdays or month_days is not None:
            raise InvalidRecurringOrderScheduleError
        return _normalize_values(weekdays, minimum=1, maximum=7), None

    if not month_days or weekdays is not None:
        raise InvalidRecurringOrderScheduleError
    return None, _normalize_values(month_days, minimum=1, maximum=31)


def validate_items(items_count: int, quantities: list[int]) -> None:
    if items_count == 0:
        raise RecurringOrderHasNoItemsError
    if any(quantity <= 0 for quantity in quantities):
        raise RecurringOrderItemQuantityError


def _normalize_values(
    values: list[int], *, minimum: int, maximum: int
) -> list[int]:
    if len(set(values)) != len(values):
        raise InvalidRecurringOrderScheduleError
    if any(value < minimum or value > maximum for value in values):
        raise InvalidRecurringOrderScheduleError
    return sorted(values)
