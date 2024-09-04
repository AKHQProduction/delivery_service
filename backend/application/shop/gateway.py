from abc import abstractmethod
from asyncio import Protocol

from domain.shop.entity.entity import Shop, ShopId
from domain.shop.entity.value_objects import ShopTitle


class ShopReader(Protocol):
    @abstractmethod
    async def by_id(self, shop_id: ShopId) -> Shop | None:
        raise NotImplementedError


class ShopSaver(Protocol):
    @abstractmethod
    async def save(self, shop: Shop) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, shop: Shop) -> None:
        raise NotImplementedError
