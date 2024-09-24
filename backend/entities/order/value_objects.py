from dataclasses import dataclass

from entities.order.errors import InvalidOrderItemQuantityError


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class OrderItemQuantity:
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderItemQuantityError()
