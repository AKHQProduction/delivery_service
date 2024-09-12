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
