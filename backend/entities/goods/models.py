from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType
from uuid import UUID

from entities.goods.value_objects import GoodsPrice, GoodsTitle
from entities.shop.models import ShopId

GoodsId = NewType("GoodsId", UUID)


class GoodsType(StrEnum):
    WATER = auto()
    OTHER = auto()


@dataclass
class Goods:
    goods_id: GoodsId | None
    shop_id: ShopId
    title: GoodsTitle
    price: GoodsPrice
    goods_type: GoodsType
    metadata_path: str | None = None
