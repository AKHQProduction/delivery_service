from dataclasses import dataclass
from decimal import Decimal

from delivery_service.domain.shared.errors import (
    ValueMustBePositiveError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Price:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueMustBePositiveError()
