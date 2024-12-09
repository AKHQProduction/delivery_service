import re
from dataclasses import dataclass

from entities.user.errors import InvalidPhoneNumberError


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        pattern = r"^\+380\d{9}$"

        if not re.match(pattern, self.value):
            raise InvalidPhoneNumberError(self.value)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class UserAddress:
    city: str
    street: str
    house_number: str
    apartment_number: int | None
    floor: int | None
    intercom_code: int | None

    @property
    def full_address(self) -> str | None:
        return (
            f"{self.city}, {self.street} {self.house_number}"
            if self.city
            else None
        )
