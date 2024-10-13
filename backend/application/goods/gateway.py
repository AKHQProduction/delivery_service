from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass

from application.common.input_data import Pagination
from entities.goods.models import Goods, GoodsId, GoodsType


@dataclass(frozen=True)
class GoodsFilters:
    shop_id: int | None = None
    goods_type: GoodsType | None = None


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

    @abstractmethod
    async def all(
        self, filters: GoodsFilters, pagination: Pagination
    ) -> list[Goods]:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: GoodsFilters) -> int:
        raise NotImplementedError
