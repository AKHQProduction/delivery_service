from dataclasses import dataclass
from enum import StrEnum, auto
from typing import NewType

from entities.goods.value_objects import GoodsTitle
from entities.order.value_objects import OrderItemAmount, OrderTotalPrice
from entities.shop.models import ShopId
from entities.user.models import UserId

OrderId = NewType("OrderId", int)
OrderItemId = NewType("OrderItemId", int)


class OrderStatus(StrEnum):
    NEW = auto()


@dataclass
class Order:
    order_id: OrderId | None
    user_id: UserId
    shop_id: ShopId
    status: OrderStatus
    total_price: OrderTotalPrice | None


@dataclass
class OrderItem:
    order_item_id: OrderItemId | None
    order_id: OrderId
    goods_title: GoodsTitle
    amount: OrderItemAmount
