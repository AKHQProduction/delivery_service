from dataclasses import dataclass

from delivery_service.domain.shared.errors import (
    ConflictError,
    ValidationError,
)
from delivery_service.domain.shared.user_id import UserID


@dataclass(eq=False)
class ShopCreationNotAllowedError(ConflictError):
    user_id: UserID

    @property
    def message(self) -> str:
        return f"User with ID={self.user_id} already has shop"


@dataclass(eq=False)
class InvalidDayOfWeekError(ValidationError):
    @property
    def message(self) -> str:
        return "Day of week must be greate than 0 but less than 7"


@dataclass(eq=False)
class UserAlreadyInStaffError(ConflictError):
    user_id: UserID

    @property
    def message(self) -> str:
        return f"User {self.user_id} already employee"


@dataclass(eq=False)
class UserNotFoundInShopStaffError(ConflictError):
    user_id: UserID

    @property
    def message(self) -> str:
        return f"User {self.user_id} not found in employees"


@dataclass(eq=False)
class CantDiscardYourselfError(ConflictError):
    pass
