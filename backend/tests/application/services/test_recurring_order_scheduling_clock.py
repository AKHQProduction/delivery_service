from datetime import date

from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.vars import ScheduleType


def test_scheduling_clock_uses_kyiv_today_for_run_window(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )

    clock = RecurringOrderSchedulingClock()

    assert clock.run_dates(
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1, 3, 5],
        month_days=None,
        include_today=False,
    ) == [
        date(2026, 5, 11),
        date(2026, 5, 13),
        date(2026, 5, 15),
        date(2026, 5, 18),
        date(2026, 5, 20),
        date(2026, 5, 22),
    ]


def test_scheduling_clock_future_order_cutoff_starts_tomorrow(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )

    assert RecurringOrderSchedulingClock().future_order_cutoff() == date(
        2026, 5, 9
    )
