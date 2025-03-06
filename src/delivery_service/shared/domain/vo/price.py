from dataclasses import dataclass
from decimal import Decimal

from delivery_service.shared.domain.errors import PriceMustBeGreateError


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Price:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise PriceMustBeGreateError()
