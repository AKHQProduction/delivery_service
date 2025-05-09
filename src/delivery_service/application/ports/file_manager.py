from abc import abstractmethod
from typing import Protocol

from delivery_service.application.query.ports.order_gateway import (
    OrderReadModel,
)


class FileManager(Protocol):
    @abstractmethod
    def create_order_files(self, orders: list[OrderReadModel]) -> bytes:
        raise NotImplementedError
