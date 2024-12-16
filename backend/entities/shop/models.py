from dataclasses import dataclass, field
from datetime import date
from typing import NewType

from entities.common.entity import BaseEntity
from entities.shop.value_objects import (
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
    regular_days_off: list[int] = field(default_factory=list)
    special_days_off: list[date] = field(default_factory=list)
    is_active: bool = True

    users: list[User] = field(default_factory=list)
