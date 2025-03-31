from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType
from uuid import UUID

from entities.common.entity import BaseEntity
from entities.common.vo import Price
from entities.goods.value_objects import GoodsTitle
from entities.shop.models import ShopId

GoodsId = NewType("GoodsId", UUID)


class GoodsType(StrEnum):
    WATER = auto()
    OTHER = auto()


@dataclass
class Goods(BaseEntity[GoodsId]):
    shop_id: ShopId
    title: GoodsTitle
    price: Price
    goods_type: GoodsType
    metadata_path: str | None = None
