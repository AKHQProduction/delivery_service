from dataclasses import dataclass

from delivery_service.domain.shared.errors import (
    ValueMustBePositiveError,
)
from delivery_service.domain.shared.new_types import FixedDecimal


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Price:
    value: FixedDecimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueMustBePositiveError()

    def __add__(self, other: "Price") -> "Price":
        return Price(self.value + other.value)

    def __sub__(self, other: "Price") -> "Price":
        return Price(self.value - other.value)

    def __mul__(self, other: "FixedDecimal") -> "Price":
        return Price(self.value * other)

    def __truediv__(self, other: "FixedDecimal") -> "Price":
        return Price(self.value / other)
