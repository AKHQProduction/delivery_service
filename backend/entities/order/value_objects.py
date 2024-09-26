from dataclasses import dataclass
from decimal import Decimal

from entities.order.errors import (
    InvalidOrderItemQuantityError,
    InvalidOrderTotalPriceError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class OrderItemAmount:
    quantity: int
    price_per_item: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderItemQuantityError()

    def total_price(self) -> Decimal:
        return self.quantity * self.price_per_item


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class OrderTotalPrice:
    price: Decimal

    def __post_init__(self) -> None:
        if self.price < 0:
            raise InvalidOrderTotalPriceError()
