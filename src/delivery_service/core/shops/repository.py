from abc import abstractmethod
from typing import Protocol

from delivery_service.core.shops.shop import Shop


class ShopRepository(Protocol):
    @abstractmethod
    def add(self, shop: Shop) -> None:
        raise NotImplementedError
