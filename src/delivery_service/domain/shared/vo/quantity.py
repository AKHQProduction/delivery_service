from dataclasses import dataclass

from delivery_service.domain.shared.errors import (
    ValueMustBePositiveError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueMustBePositiveError()

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(value=self.value + other.value)

    def __sub__(self, other: "Quantity") -> "Quantity":
        return Quantity(value=self.value - other.value)
