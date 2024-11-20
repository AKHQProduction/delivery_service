import re
from dataclasses import dataclass, field
from datetime import date, datetime

from zoneinfo import ZoneInfo

from entities.shop.errors import (
    InvalidBotTokenError,
    InvalidDeliveryDistanceError,
    InvalidRegularDayOffError,
    InvalidSpecialDayOffError,
    ShopTitleTooLongError,
    ShopTitleTooShortError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class ShopToken:
    value: str

    def __post_init__(self) -> None:
        pattern = r"^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$"

        if not re.match(pattern, self.value):
            raise InvalidBotTokenError(self.value)


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

    MONDAY = 0
    SUNDAY = 6

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
class DeliveryDistance:
    kilometers: int

    def __post_init__(self) -> None:
        if self.kilometers <= 0:
            raise InvalidDeliveryDistanceError()


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class ShopLocation:
    latitude: float
    longitude: float
