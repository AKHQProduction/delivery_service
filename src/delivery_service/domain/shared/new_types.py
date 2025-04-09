from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from enum import Enum
from typing import Any, Union


class Empty(Enum):
    UNSET = "UNSET"


class FixedDecimal(Decimal):
    """Special type of decimal with rounded to 2 decimal places"""

    def __new__(cls, value: Union[float, str, Decimal]):
        try:
            new_decimal = super().__new__(cls, value)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Incorrect value for Decimal: {value}") from e

        quantized = new_decimal.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return super().__new__(cls, str(quantized))

    def __add__(self, other: Any) -> "FixedDecimal":
        return FixedDecimal(super().__add__(other))

    def __sub__(self, other: Any) -> "FixedDecimal":
        return FixedDecimal(super().__sub__(other))

    def __mul__(self, other: Any) -> "FixedDecimal":
        return FixedDecimal(super().__mul__(other))

    def __truediv__(self, other: Any) -> "FixedDecimal":
        return FixedDecimal(super().__truediv__(other))
