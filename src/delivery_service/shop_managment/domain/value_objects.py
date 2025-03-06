from dataclasses import dataclass, field
from datetime import date

from delivery_service.shop_managment.domain.errors import InvalidDayOfWeekError

MONDAY = 0
SATURDAY = 6


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class DaysOff:
    regular_days_off: list[int] = field(default_factory=list)
    irregular_days_off: list[date] = field(default_factory=list)

    def __post_init__(self) -> None:
        if (
            min(self.regular_days_off) < MONDAY
            or max(self.regular_days_off) > SATURDAY
        ):
            raise InvalidDayOfWeekError()

    def change_regular_days_off(
        self, new_regular_days_off: list[int]
    ) -> "DaysOff":
        return DaysOff(
            regular_days_off=new_regular_days_off,
            irregular_days_off=self.irregular_days_off,
        )

    def can_deliver_in_this_day(self, day: date) -> bool:
        weekday = day.weekday()

        return bool(
            weekday not in self.regular_days_off
            and day not in self.irregular_days_off
        )
