from dataclasses import dataclass

from domain.common.errors.base import DomainError


@dataclass(eq=False)
class InvalidPhoneNumber(DomainError, ValueError):
    phone_number: str

    @property
    def message(self):
        return f"Invalid phone number {self.phone_number}"
