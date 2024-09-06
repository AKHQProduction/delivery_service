from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType

from entities.shop.value_objects import RegularDaysOff, ShopTitle, ShopToken
from entities.user.model import User, UserId

ShopId = NewType("ShopId", int)


@dataclass
class Shop:
    shop_id: ShopId | None
    title: ShopTitle
    token: ShopToken
    regular_days_off: RegularDaysOff = field(default_factory=list)
    special_days_off: list[datetime] = field(default_factory=list)
    is_active: bool = True

    users: list[User] = field(default_factory=list)
