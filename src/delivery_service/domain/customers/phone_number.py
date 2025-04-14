import re
from dataclasses import dataclass

from delivery_service.domain.shared.errors import ValidationError

PHONE_NUMBER_PATTERN = re.compile(r"^\+380\d{9}$")


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        if not PHONE_NUMBER_PATTERN.match(self.value):
            raise ValidationError()


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class PhoneBook:
    primary: PhoneNumber
    secondary: PhoneNumber | None = None

    def change_primary_number(self, phone_number: str) -> "PhoneBook":
        return PhoneBook(
            primary=PhoneNumber(phone_number), secondary=self.secondary
        )

    def change_secondary_number(self, phone_number: str | None) -> "PhoneBook":
        return PhoneBook(
            primary=self.primary,
            secondary=PhoneNumber(phone_number) if phone_number else None,
        )
