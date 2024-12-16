from dataclasses import dataclass
from typing import Sequence

from application.common.persistence.goods import (
    GoodsReader,
    GoodsReaderFilters,
)
from application.common.persistence.shop import ShopGateway
from application.common.persistence.view_models import GoodsView


@dataclass(frozen=True)
class GetManyGoodsQuery:
    filters: GoodsReaderFilters


@dataclass
class GetManyGoodsQueryHandler:
    goods_reader: GoodsReader
    shop_gateway: ShopGateway

    async def __call__(self, query: GetManyGoodsQuery) -> Sequence[GoodsView]:
        return await self.goods_reader.read_many(query.filters)
