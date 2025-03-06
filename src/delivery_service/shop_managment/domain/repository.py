from abc import abstractmethod
from typing import Protocol

from delivery_service.shop_managment.domain.shop import Shop


class ShopRepository(Protocol):
    @abstractmethod
    def add(self, shop: Shop) -> None:
        raise NotImplementedError
