from dataclasses import dataclass
from typing import NewType

from entities.profile.value_objects import PhoneNumber, UserAddress
from entities.shop.models import ShopId
from entities.user.models import UserId

ProfileId = NewType("ProfileId", int)


@dataclass
class Profile:
    profile_id: ProfileId | None
    full_name: str
    shop_id: ShopId | None = None
    user_address: UserAddress | None = None
    user_id: UserId | None = None
    phone_number: PhoneNumber | None = None
