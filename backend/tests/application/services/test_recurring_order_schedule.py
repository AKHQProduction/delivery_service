from datetime import date

from backend.application.services.recurring.schedule import (
    iter_recurring_order_dates,
)
from backend.application.vars import ScheduleType


def test_weekly_schedule_defaults_to_tomorrow_through_today_plus_14() -> None:
    base_date = date(2026, 5, 8)

    result = iter_recurring_order_dates(
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1, 3, 5],
        month_days=None,
        base_date=base_date,
        include_today=False,
    )

    assert result == [
        date(2026, 5, 11),
        date(2026, 5, 13),
        date(2026, 5, 15),
        date(2026, 5, 18),
        date(2026, 5, 20),
        date(2026, 5, 22),
    ]


def test_weekly_schedule_can_include_today_when_today_matches() -> None:
    result = iter_recurring_order_dates(
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[5],
        month_days=None,
        base_date=date(2026, 5, 8),
        include_today=True,
    )

    assert result == [
        date(2026, 5, 8),
        date(2026, 5, 15),
        date(2026, 5, 22),
    ]


def test_weekly_schedule_does_not_include_non_matching_today() -> None:
    result = iter_recurring_order_dates(
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        base_date=date(2026, 5, 8),
        include_today=True,
    )

    assert result == [date(2026, 5, 11), date(2026, 5, 18)]


def test_monthly_by_day_schedule_matches_month_days_across_window() -> None:
    result = iter_recurring_order_dates(
        schedule_type=ScheduleType.MONTHLY_BY_DAY,
        weekdays=None,
        month_days=[1, 13],
        base_date=date(2026, 5, 30),
        include_today=False,
    )

    assert result == [date(2026, 6, 1), date(2026, 6, 13)]
