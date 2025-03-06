from abc import abstractmethod
from typing import Protocol

from delivery_service.shared.domain.shop_id import ShopID


class ShopIDGenerator(Protocol):
    @abstractmethod
    def generate_shop_id(self) -> ShopID:
        raise NotImplementedError
