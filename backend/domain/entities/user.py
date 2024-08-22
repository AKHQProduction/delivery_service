from dataclasses import dataclass
from enum import Enum
from typing import Union

from domain.value_objects.phone_number import PhoneNumber
from domain.value_objects.user_id import UserId


class RoleName(Enum):
    BLOCKER = "BLOCKED"
    USER = "USER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    DRIVER = "DRIVER"


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

    @property
    def formatted_username(self) -> str:
        return "Відсутній" if self.username is None else f"@{self.username}"

    @property
    def formatted_phone_number(self) -> str:
        return "Відсутній" if self.phone_number is None else self.phone_number.to_raw()

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
