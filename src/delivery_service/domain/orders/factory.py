from abc import abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from delivery_service.domain.orders.order import Order


@dataclass(frozen=True)
class OrderLineData:
    title: str
    price: Decimal
    quantity: int


class OrderFactory(Protocol):
    @abstractmethod
    def create_new_order(self, order_lines_data: list[OrderLineData]) -> Order:
        raise NotImplementedError
