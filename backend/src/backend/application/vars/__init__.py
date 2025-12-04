from enum import StrEnum
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
ShopId = NewType("ShopId", UUID)
ProductId = NewType("ProductId", UUID)
ClientId = NewType("ClientId", UUID)


class ShopRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    COURIER = "COURIER"


class ProductCategory(StrEnum):
    WATER = "WATER"
    OTHER = "OTHER"


class AddressType(StrEnum):
    APARTMENT = "APARTMENT"
    PRIVATE_HOUSE = "PRIVATE_HOUSE"
