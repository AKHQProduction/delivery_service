from dataclasses import dataclass
from typing import NewType

from entities.common.entity import BaseEntity
from entities.user.value_objects import UserAddress

UserId = NewType("UserId", int)


@dataclass(eq=False)
class User(BaseEntity[UserId]):
    full_name: str
    tg_id: int | None = None
    username: str | None = None
    user_address: UserAddress | None = None
    phone_number: str | None = None
    is_active: bool = True
