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


class NewItemSchema(BaseModel):
    product_id: ProductId
    quantity: int


class ItemToUpdateSchema(BaseModel):
    item_id: OrderItemId
    quantity: int | None = None
    price_per_item: int | None = None
    name: str | None = None


class UpdateOrderSchema(BaseModel):
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items_to_add: list[NewItemSchema] | None = None
    items_to_update: list[ItemToUpdateSchema] | None = None
    items_to_delete: list[OrderItemId] | None = None
