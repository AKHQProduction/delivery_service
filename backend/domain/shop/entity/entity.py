from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType

from domain.shop.entity.value_objects import ShopTitle, ShopToken
from domain.user.entity.user import UserId

ShopId = NewType("ShopId", int)


@dataclass
class Shop:
    shop_id: ShopId | None
    user_id: UserId
    title: ShopTitle
    token: ShopToken
    regular_days_off: list[int] = field(default_factory=list)
    special_days_off: list[datetime] = field(default_factory=list)
    is_active: bool = True
