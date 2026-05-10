from datetime import date, timedelta

from backend.application.vars import ScheduleType

RUN_WINDOW_DAYS = 14


def iter_recurring_order_dates(
    *,
    schedule_type: ScheduleType,
    weekdays: list[int] | None,
    month_days: list[int] | None,
    base_date: date,
    include_today: bool,
) -> list[date]:
    start_date = base_date if include_today else base_date + timedelta(days=1)
    end_date = base_date + timedelta(days=RUN_WINDOW_DAYS)

    result: list[date] = []
    cursor = start_date
    while cursor <= end_date:
        if _matches_date(
            cursor,
            schedule_type=schedule_type,
            weekdays=weekdays,
            month_days=month_days,
        ):
            result.append(cursor)
        cursor += timedelta(days=1)

    return result


def _matches_date(
    current_date: date,
    *,
    schedule_type: ScheduleType,
    weekdays: list[int] | None,
    month_days: list[int] | None,
) -> bool:
    if schedule_type == ScheduleType.WEEKLY:
        return weekdays is not None and current_date.isoweekday() in weekdays

    return month_days is not None and current_date.day in month_days
