from dataclasses import dataclass, field
from datetime import date, datetime

from zoneinfo import ZoneInfo

from entities.shop.errors import (
    InvalidRegularDayOffError,
    InvalidSpecialDayOffError,
    ShopTitleTooLongError,
    ShopTitleTooShortError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class ShopTitle:
    title: str

    MAX_TITLE_LEN = 20
    MIN_TITLE_LEN = 3

    def __post_init__(self) -> None:
        len_value = len(self.title)

        if len_value <= self.MIN_TITLE_LEN:
            raise ShopTitleTooShortError(self.title)

        if len_value > self.MAX_TITLE_LEN:
            raise ShopTitleTooLongError(self.title)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class RegularDaysOff:
    regular_days: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if any(
            day < self.MONDAY or day > self.SUNDAY for day in self.regular_days
        ):
            raise InvalidRegularDayOffError()


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class SpecialDaysOff:
    special_days: list[date] = field(default_factory=list)

    def __post_init__(self) -> None:
        now = datetime.now(tz=ZoneInfo("Europe/Kiev")).date()

        if any(now > day for day in self.special_days):
            raise InvalidSpecialDayOffError()


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class DaysOff:
    regular_days: list[int] = field(default_factory=list)
    special_days: list[date] = field(default_factory=list)

    def __post_init__(self) -> None:
        monday = 0
        sunday = 6
        now = datetime.now(tz=ZoneInfo("Europe/Kiev")).date()

        if any(now > day for day in self.special_days):
            raise InvalidSpecialDayOffError()

        if any(day < monday or day > sunday for day in self.regular_days):
            raise InvalidRegularDayOffError()

    def can_receive_orders(self, order_date: date) -> bool:
        return (
            order_date.day not in self.regular_days
            or order_date not in self.special_days
        )


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class ShopLocation:
    latitude: float
    longitude: float
