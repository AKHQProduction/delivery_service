from abc import abstractmethod
from typing import Protocol

from delivery_service.application.query.ports.order_gateway import (
    OrderReadModel,
)
from delivery_service.domain.orders.order import DeliveryPreference


class FileManager(Protocol):
    @abstractmethod
    def create_order_files(
        self, orders: dict[DeliveryPreference, list[OrderReadModel]]
    ) -> dict[DeliveryPreference, bytes]:
        raise NotImplementedError
