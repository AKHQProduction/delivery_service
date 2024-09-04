import re
from dataclasses import dataclass

from entities.shop.errors import (
    InvalidBotTokenError,
    ShopTitleTooLongError,
    ShopTitleTooShortError
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

    def __post_init__(self) -> None:
        len_value = len(self.title)

        if len_value <= 3:
            ShopTitleTooShortError(self.title)

        if len_value >= 20:
            ShopTitleTooLongError(self.title)
