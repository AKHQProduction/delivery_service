from dataclasses import dataclass
from typing import NewType

from entities.user.value_objects import PhoneNumber, UserAddress

UserId = NewType("UserId", int)


@dataclass
class User:
    user_id: UserId
    full_name: str
    username: str | None = None
    user_address: UserAddress | None = None
    phone_number: PhoneNumber | None = None
    is_active: bool = True
