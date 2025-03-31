from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.shop_id import ShopID


class ShopProvider(Protocol):
    @abstractmethod
    async def get_current_shop_id(self) -> ShopID:
        raise NotImplementedError
