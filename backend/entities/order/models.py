from dataclasses import dataclass
from datetime import date
from enum import StrEnum, auto
from typing import NewType

from entities.order.value_objects import (
    BottlesToExchange,
    OrderItemAmount,
    OrderTotalPrice,
)
from entities.profile.models import ProfileId
from entities.shop.models import ShopId

OrderId = NewType("OrderId", int)
OrderItemId = NewType("OrderItemId", int)


class OrderStatus(StrEnum):
    NEW = auto()


class DeliveryPreference(StrEnum):
    MORNING = auto()
    AFTERNOON = auto()


@dataclass
class Order:
    order_id: OrderId | None
    profile_id: ProfileId
    shop_id: ShopId
    status: OrderStatus
    total_price: OrderTotalPrice
    delivery_preference: DeliveryPreference
    bottles_to_exchange: BottlesToExchange
    delivery_date: date


@dataclass
class OrderItem:
    order_item_id: OrderItemId | None
    order_id: OrderId
    order_item_title: str
    amount: OrderItemAmount
