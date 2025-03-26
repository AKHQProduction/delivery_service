from dataclasses import dataclass

from delivery_service.shared.domain.errors import (
    ValidationError,
)


@dataclass(eq=False)
class InvalidFullNameError(ValidationError):
    @property
    def message(self) -> str:
        return "Invalid full name length"


@dataclass(eq=False)
class FullNameTooLongError(ValidationError):
    @property
    def message(self) -> str:
        return "Full name cannot exceed 128 characters"
