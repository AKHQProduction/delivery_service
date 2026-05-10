import logging
from datetime import date, timedelta

from backend.application.services.recurring.schedule import (
    iter_recurring_order_dates,
)
from backend.application.vars import ScheduleType, today

logger = logging.getLogger(__name__)


class RecurringOrderSchedulingClock:
    def today(self) -> date:
        return today()

    def future_order_cutoff(self) -> date:
        return self.today() + timedelta(days=1)

    def run_dates(
        self,
        *,
        schedule_type: ScheduleType,
        weekdays: list[int] | None,
        month_days: list[int] | None,
        include_today: bool,
    ) -> list[date]:
        dates = iter_recurring_order_dates(
            schedule_type=schedule_type,
            weekdays=weekdays,
            month_days=month_days,
            base_date=self.today(),
            include_today=include_today,
        )
        logger.debug(
            "Calculated recurring order run dates: "
            "schedule_type=%s weekdays=%s month_days=%s include_today=%s "
            "dates=%s",
            schedule_type,
            weekdays,
            month_days,
            include_today,
            dates,
        )
        return dates
