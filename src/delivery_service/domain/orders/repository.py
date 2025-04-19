from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.orders.order import Order


class OrderRepository(Protocol):
    @abstractmethod
    def add(self, new_order: Order) -> None:
        raise NotImplementedError
