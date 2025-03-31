from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from application.common.persistence.view_models import GoodsView
from entities.goods.models import Goods, GoodsId, GoodsType
from entities.shop.models import ShopId


class GoodsGateway(Protocol):
    @abstractmethod
    async def is_exist(self, title: str, shop_id: ShopId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_id(self, goods_id: GoodsId) -> Goods | None:
        raise NotImplementedError


@dataclass(frozen=True)
class GoodsReaderFilters:
    shop_id: int | None
    goods_type: GoodsType | None = None


class GoodsReader(Protocol):
    @abstractmethod
    async def read_with_id(self, goods_id: UUID) -> Goods | None:
        raise NotImplementedError

    @abstractmethod
    async def read_many(
        self, filters: GoodsReaderFilters
    ) -> Sequence[GoodsView]:
        raise NotImplementedError
