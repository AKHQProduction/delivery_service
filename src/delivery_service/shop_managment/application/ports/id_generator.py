from abc import abstractmethod
from typing import Protocol

from delivery_service.shop_managment.domain.shop import ShopID


class ShopIDGenerator(Protocol):
    @abstractmethod
    def generate_shop_id(self) -> ShopID:
        raise NotImplementedError
