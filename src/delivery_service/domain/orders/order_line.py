from dataclasses import dataclass

from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.order_line_id import OrderLineID
from delivery_service.domain.shared.vo.price import Price
from delivery_service.domain.shared.vo.quantity import Quantity


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class OrderLABCine:
    title: str
    price_per_item: Price
    quantity: Quantity


class OrderLine(Entity[OrderLineID]):
    def __init__(self, order_line_id: OrderLineID) -> None:
        super().__init__(entity_id=order_line_id)
