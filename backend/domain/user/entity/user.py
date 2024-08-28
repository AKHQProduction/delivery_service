from dataclasses import dataclass
from enum import Enum
from typing import Union

from domain.user.value_objects.phone_number import PhoneNumber
from domain.user.value_objects.user_id import UserId


class RoleName(Enum):
    BLOCKER = "🚫 Заблокований"
    USER = "🙎‍♂️ Користувач"
    ADMIN = "🤴 Адмін"
    MANAGER = "👩‍💻 Менеджер"
    DRIVER = "🚛 Водій"


@dataclass
class User:
    user_id: UserId
    full_name: str
    role: RoleName = RoleName.USER
    username: str | None = None
    phone_number: PhoneNumber | None = None
    is_active: bool = True

    def change_role(self, role: RoleName) -> None:
        self.role = role

    def __hash__(self) -> int:
        return hash(self.user_id)

    def __eq__(self, other: Union[object, "User"]) -> bool:
        if not isinstance(other, User):
            return False

        return self.user_id == other.user_id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__} object(id={self.user_id}, "
            f"is_active={bool(self)})"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__} <{self.user_id}>"
