from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from entities.common.errors import InvalidPriceError, InvalidQuantityError


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Price:
    value: Decimal | str

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

    def __repr__(self) -> str:
        return self.__str__()


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidQuantityError()

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()
