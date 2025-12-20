from datetime import date

from pydantic import BaseModel

from backend.application.vars import (
    AddressId,
    ClientId,
    Empty,
    OrderItemId,
    PhoneId,
    ProductId,
    TimePreference,
)


class OrderItemSchema(BaseModel):
    quantity: int
    product_id: ProductId | None = None
    id: OrderItemId | None = None


class UpdateOrderSchema(BaseModel):
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items: list[OrderItemSchema] | None = None
