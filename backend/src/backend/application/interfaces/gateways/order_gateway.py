from dataclasses import dataclass
from datetime import date
from typing import Protocol

from backend.application.vars import (
    AddressType,
    ClientId,
    OrderId,
    OrderItemId,
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
    name: str
    quantity: int
    price_per_item: int
    id: OrderItemId | None = None


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


class OrderGateway(Protocol):
    def next_id(self) -> OrderId:
        raise NotImplementedError

    async def create_order(self, dto: CreateOrderDTO) -> None:
        raise NotImplementedError
