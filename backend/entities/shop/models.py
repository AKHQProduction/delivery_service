from dataclasses import dataclass, field
from typing import NewType

from entities.shop.value_objects import (
    DeliveryDistance,
    RegularDaysOff,
    ShopLocation,
    ShopTitle,
    ShopToken,
    SpecialDaysOff,
)
from entities.user.models import User

ShopId = NewType("ShopId", int)


@dataclass
class Shop:
    shop_id: ShopId | None
    title: ShopTitle
    token: ShopToken
    delivery_distance: DeliveryDistance
    location: ShopLocation
    regular_days_off: RegularDaysOff = field(default_factory=RegularDaysOff)
    special_days_off: SpecialDaysOff = field(default_factory=SpecialDaysOff)
    is_active: bool = True

    users: list[User] = field(default_factory=list)
