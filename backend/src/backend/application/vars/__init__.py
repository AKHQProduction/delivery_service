from enum import StrEnum
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
ShopId = NewType("ShopId", UUID)


class ShopRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    COURIER = "COURIER"
