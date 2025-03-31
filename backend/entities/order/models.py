from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum, auto
from typing import NewType

from entities.common.entity import BaseEntity
from entities.common.vo import Price, Quantity
from entities.shop.models import ShopId
from entities.user.models import UserId

OrderId = NewType("OrderId", int)
OrderItemId = NewType("OrderItemId", int)


class OrderStatus(StrEnum):
    NEW = auto()
    IN_PROGRESS = auto()
    CANCELED = auto()
    DELIVERED = auto()


class DeliveryPreference(StrEnum):
    MORNING = auto()
    AFTERNOON = auto()


@dataclass
class OrderItem(BaseEntity[OrderItemId]):
    order_id: OrderId
    order_item_title: str
    quantity: Quantity
    price_per_item: Price


@dataclass
class Order(BaseEntity[OrderId]):
    user_id: UserId
    shop_id: ShopId
    status: OrderStatus
    delivery_preference: DeliveryPreference
    bottles_to_exchange: Quantity
    delivery_date: date
    order_items: list[OrderItem] = field(default_factory=list)
