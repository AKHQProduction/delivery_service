from abc import abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import (
    AddressType,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    ProductId,
    ShopId,
    TimePreference,
)


@dataclass(frozen=True)
class DeliveryAddressDTO:
    street: str
    house: str
    address_type: AddressType
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None


@dataclass(frozen=True)
class OrderItemDTO:
    quantity: int
    name: str | None = None
    price_per_item: int | None = None
    id: OrderItemId | None = None
    product_id: ProductId | None = None


@dataclass(frozen=True)
class CreateOrderDTO:
    order_id: OrderId
    shop_id: ShopId
    client_id: ClientId
    delivery_date: date
    time_preference: TimePreference
    delivery_phone: str
    delivery_address: DeliveryAddressDTO
    order_items: list[OrderItemDTO]
    comment: str | None


@dataclass
class Order:
    order_id: OrderId
    shop_id: ShopId
    client_id: ClientId
    delivery_date: date
    time_preference: TimePreference
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
    date: date
    time_preference: TimePreference
    delivery_phone: str
    delivery_address: DeliveryAddressDTO
    comment: str | None
    client_id: ClientId
    client_name: str
    items: list[OrderItemReadModel]


@dataclass(frozen=True)
class GetOrdersFilters:
    shop_id: ShopId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    client_name: str | None = None
    custom_id: str | None = None


@dataclass(frozen=True)
class UpdateOrderDTO:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    delivery_phone: str | None = None
    delivery_address: DeliveryAddressDTO | None = None
    comment: str | Empty | None = None
    items: list[OrderItemDTO] | None = None


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
