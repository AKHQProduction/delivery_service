from dataclasses import dataclass
from enum import Enum
from typing import NewType, Union

from domain.user.value_objects.phone_number import PhoneNumber


class RoleName(Enum):
    BLOCKER = "🚫 Заблокований"
    USER = "🙎‍♂️ Користувач"
    ADMIN = "🤴 Адмін"
    MANAGER = "👩‍💻 Менеджер"
    DRIVER = "🚛 Водій"


UserId = NewType("UserId", int)


@dataclass
class User:
    user_id: UserId
    full_name: str
    role: RoleName = RoleName.USER
    username: str | None = None
    phone_number: PhoneNumber | None = None
    is_active: bool = True
