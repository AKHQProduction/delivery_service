from abc import abstractmethod
from typing import Protocol

from delivery_service.products_management.domain.product import ProductID


class ProductIDGenerator(Protocol):
    @abstractmethod
    def generate_product_id(self) -> ProductID:
        raise NotImplementedError
