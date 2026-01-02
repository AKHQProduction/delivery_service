from enum import StrEnum
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
ShopId = NewType("ShopId", UUID)
ProductId = NewType("ProductId", UUID)
CategoryId = NewType("CategoryId", UUID)
ClientId = NewType("ClientId", UUID)
OrderId = NewType("OrderId", UUID)
OrderItemId = NewType("OrderItemId", int)
AddressId = NewType("AddressId", int)
PhoneId = NewType("PhoneId", int)


class ShopRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    COURIER = "COURIER"


class AddressType(StrEnum):
    APARTMENT = "APARTMENT"
    PRIVATE_HOUSE = "PRIVATE_HOUSE"


class TimePreference(StrEnum):
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"


class Empty(StrEnum):
    EMPTY = "EMPTY"
