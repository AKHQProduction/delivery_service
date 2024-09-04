from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType

from entities.user.value_objects import PhoneNumber


class RoleName(Enum):
    BLOCKER = auto()
    USER = auto()
    ADMIN = auto()
    MANAGER = auto()
    DRIVER = auto()


UserId = NewType("UserId", int)


@dataclass
class User:
    user_id: UserId
    full_name: str
    role: RoleName = RoleName.USER
    username: str | None = None
    phone_number: PhoneNumber | None = None
    is_active: bool = True
