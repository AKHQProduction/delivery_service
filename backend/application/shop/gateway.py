from abc import abstractmethod
from asyncio import Protocol

from entities.shop.models import Shop, ShopId
from entities.user.models import UserId


class ShopReader(Protocol):
    @abstractmethod
    async def by_id(self, shop_id: ShopId) -> Shop | None:
        raise NotImplementedError

    @abstractmethod
    async def by_identity(self, user_id: UserId) -> Shop | None:
        raise NotImplementedError


class ShopSaver(Protocol):
    @abstractmethod
    async def save(self, shop: Shop) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, shop_id: ShopId) -> None:
        raise NotImplementedError
