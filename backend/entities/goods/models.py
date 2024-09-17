from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from entities.goods.value_objects import GoodsMetadata, GoodsPrice, GoodsTitle
from entities.shop.models import ShopId

GoodsId = NewType("GoodsId", UUID)


@dataclass
class Goods:
    goods_id: GoodsId | None
    shop_id: ShopId
    title: GoodsTitle
    price: GoodsPrice
    metadata: GoodsMetadata | None = None
