from collections.abc import Sequence
from dataclasses import dataclass

from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerReadModel,
)
from delivery_service.domain.orders.order_ids import OrderID, OrderLineID
from delivery_service.domain.orders.value_object import AvailableTimeSlot
from delivery_service.domain.shared.new_types import FixedDecimal


@dataclass(frozen=True)
class OrderLineReadModel:
    order_line_id: OrderLineID
    title: str
    price_per_item: FixedDecimal
    quantity: int


@dataclass(frozen=True)
class OrderReadModel:
    order_id: OrderID
    customer: CustomerReadModel
    time_slot: AvailableTimeSlot
    delivery_date: str
    order_lines: Sequence[OrderLineReadModel]
    total_order_price: FixedDecimal
    address: AddressReadModel | None = None
