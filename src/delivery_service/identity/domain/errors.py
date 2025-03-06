from dataclasses import dataclass

from delivery_service.shared.domain.errors import (
    EntityAlreadyExistsError,
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


@dataclass(eq=False)
class UserAlreadyExistsError(EntityAlreadyExistsError):
    telegram_id: int

    @property
    def message(self) -> str:
        return f"User with telegram id={self.telegram_id} already exists"
