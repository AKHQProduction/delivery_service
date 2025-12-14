from abc import abstractmethod
from datetime import date
from typing import Protocol

from backend.application.interfaces.gateways.order_gateway import (
    OrderReadModel,
)


class OrdersPDFGenerator(Protocol):
    @abstractmethod
    def handle(
        self,
        orders: list[OrderReadModel],
        delivery_date: date,
        shop_name: str,
    ) -> bytes:
        raise NotImplementedError
