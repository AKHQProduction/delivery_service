from dataclasses import dataclass
from typing import NewType

from entities.shop.models import ShopId
from entities.user.models import UserId

ProfileId = NewType("ProfileId", int)


@dataclass
class Profile:
    profile_id: ProfileId | None
    shop_id: ShopId | None = None
    user_id: UserId | None = None
