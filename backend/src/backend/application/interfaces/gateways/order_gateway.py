from abc import abstractmethod
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import (
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PaymentMethod,
    ProductId,
    ShopId,
)


@dataclass(frozen=True)
class PaymentMethodStatsReadModel:
    method: PaymentMethod
    orders_sum: int


@dataclass(frozen=True)
class DeliveryAddressDTO:
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class OrderItemDTO:
    quantity: int
    name: str | None = None
    price_per_item: Decimal | None = None
    id: OrderItemId | None = None
    product_id: ProductId | None = None


@dataclass(frozen=True)
class CreateOrderDTO:
    order_id: OrderId
    shop_id: ShopId
    client_id: ClientId
    delivery_date: date
    delivery_start_time: time
    delivery_end_time: time
    delivery_phone: str
    delivery_address: DeliveryAddressDTO
    order_items: list[OrderItemDTO]
    payment_method: PaymentMethod
    comment: str | None


@dataclass
class Order:
    order_id: OrderId
    shop_id: ShopId
    client_id: ClientId
    delivery_date: date
    delivery_start_time: time
    delivery_end_time: time
    delivery_phone: str
    delivery_address: DeliveryAddressDTO
    comment: str | None


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


@dataclass(frozen=True)
class UpdateOrderDTO:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    delivery_start_time: time | None = None
    delivery_end_time: time | None = None
    delivery_phone: str | None = None
    delivery_address: DeliveryAddressDTO | None = None
    comment: str | Empty | None = None
    items: list[OrderItemDTO] | None = None
    payment_method: PaymentMethod | None = None


class OrderGateway(Protocol):
    @abstractmethod
    def next_id(self) -> OrderId:
        raise NotImplementedError

    @abstractmethod
    async def create_order(self, dto: CreateOrderDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read(
        self, order_id: OrderId, shop_id: ShopId
    ) -> OrderReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all(
        self, filters: GetOrdersFilters, pagination: Pagination
    ) -> list[OrderReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, dto: UpdateOrderDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_items(self, order_id: OrderId) -> list[OrderItemReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_stats(
        self,
        filters: GetOrdersFilters,
        time_slots_filter: list[TimeSlotFilter],
    ) -> OrderStatsReadModel:
        raise NotImplementedError
