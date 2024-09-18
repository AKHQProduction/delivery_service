from abc import abstractmethod
from asyncio import Protocol

from entities.goods.models import Goods, GoodsId


class GoodsSaver(Protocol):
    @abstractmethod
    async def save(self, goods: Goods) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, goods: Goods) -> None:
        raise NotImplementedError


class GoodsReader(Protocol):
    @abstractmethod
    async def by_id(self, goods_id: GoodsId) -> Goods | None:
        raise NotImplementedError
