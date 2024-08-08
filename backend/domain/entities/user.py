from dataclasses import dataclass
from typing import Union

from domain.value_objects.phone_number import PhoneNumber
from domain.value_objects.user_id import UserId


@dataclass
class User:
    user_id: UserId
    full_name: str
    username: str | None = None
    phone_number: PhoneNumber | None = None
    is_active: bool = True

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
