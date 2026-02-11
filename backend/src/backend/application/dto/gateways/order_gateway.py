from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal

from backend.application.vars import (
    ClientId,
    OrderId,
    OrderItemId,
    PaymentMethod,
    ProductId,
    ShopId,
)
from backend.infrastructure.persistence.tables.base import DeliveryAddressDTO


@dataclass(frozen=True)
class PaymentMethodStatsReadModel:
    method: PaymentMethod
    orders_sum: int


@dataclass(frozen=True)
class OrderItemDTO:
    quantity: int
    name: str | None = None
    price_per_item: Decimal | None = None
    id: OrderItemId | None = None
    product_id: ProductId | None = None


@dataclass(frozen=True)
class OrderItemReadModel:
    id: int
    name: str
    quantity: int
    price_per_item: int
    product_id: ProductId | None = None


@dataclass(frozen=True)
class OrderReadModel:
    order_id: OrderId
    date: str
    time_slot: str
    delivery_phone: str
    delivery_address: DeliveryAddressDTO
    comment: str | None
    client_id: ClientId
    client_name: str
    items: list[OrderItemReadModel]
    payment_method: PaymentMethod


@dataclass(frozen=True)
class TimeSlotFilter:
    start_time: time
    end_time: time


@dataclass(frozen=True)
class GetOrdersFilters:
    shop_id: ShopId | None = None
    start_date: date | None = None
    end_date: date | None = None
    delivery_start_time: time | None = None
    client_name: str | None = None


@dataclass(frozen=True)
class CategoryStatsReadModel:
    name: str
    quantity: int


@dataclass(frozen=True)
class TimeSlotStatsReadModel:
    time_slot: str
    total: int


@dataclass(frozen=True)
class OrderStatsReadModel:
    total_orders: int
    total_orders_sum: int
    time_slot_stats: list[TimeSlotStatsReadModel]
    category_stats: list[CategoryStatsReadModel]
    payment_method_stats: list[PaymentMethodStatsReadModel]
