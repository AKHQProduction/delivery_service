from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class InvalidPhoneNumberError(DomainError, ValueError):
    phone_number: str

    @property
    def message(self):
        return f"Invalid phone number {self.phone_number}"
