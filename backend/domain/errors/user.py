from dataclasses import dataclass

from backend.domain.common.errors.base import DomainError


@dataclass(eq=False)
class InvalidPhoneNumber(DomainError):
    phone_number: str

    @property
    def message(self):
        return f"Invalid phone number {self.phone_number}"
