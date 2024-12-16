from dataclasses import dataclass, field
from typing import NewType

from entities.common.entity import BaseEntity
from entities.shop.value_objects import (
    DaysOff,
    ShopLocation,
)
from entities.user.models import User

ShopId = NewType("ShopId", int)


@dataclass(eq=False)
class Shop(BaseEntity[ShopId]):
    title: str
    token: str
    delivery_distance: int
    location: ShopLocation
    days_off: DaysOff
    is_active: bool = True

    users: list[User] = field(default_factory=list)
