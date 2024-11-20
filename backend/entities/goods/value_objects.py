from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from entities.common.errors import InvalidPriceError
from entities.goods.errors import (
    GoodsTitleTooLongError,
    GoodsTitleTooShortError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class GoodsTitle:
    title: str

    MIN_TITLE_LEN = 3
    MAX_TITLE_LEN = 20

    def __post_init__(self) -> None:
        len_value = len(self.title)

        if len_value < self.MIN_TITLE_LEN:
            raise GoodsTitleTooShortError(self.title)

        if len_value > self.MAX_TITLE_LEN:
            raise GoodsTitleTooLongError(self.title)

    def __str__(self) -> str:
        return self.title


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class GoodsPrice:
    value: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.value, str):
            try:
                object.__setattr__(self, "value", Decimal(self.value))
            except InvalidOperation as error:
                raise ValueError(
                    f"Invalid value for Decimal: {self.value}"
                ) from error

        if self.value <= 0:
            raise InvalidPriceError()

    def __str__(self) -> str:
        return f"{self.value}"
