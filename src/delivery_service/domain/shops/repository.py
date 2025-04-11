from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.shop import Shop


class ShopRepository(Protocol):
    @abstractmethod
    def add(self, shop: Shop) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, identity_id: UserID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_identity(self, identity_id: UserID) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, shop_id: ShopID) -> Shop | None:
        raise NotImplementedError
