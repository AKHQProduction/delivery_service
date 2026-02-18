from dataclasses import dataclass
from datetime import date
from typing import Any

from backend.application.vars import ClientId


class ApplicationError(Exception):
    """Base application error."""


class AuthorizationError(ApplicationError):
    @property
    def message(self) -> str:
        return "User not authorized"


class AccessDeniedError(ApplicationError):
    @property
    def message(self) -> str:
        return "Access denied to this resource"


class EntityNotFoundError(ApplicationError):
    def __init__(self, entity: str, entity_id: Any | None = None) -> None:
        self._entity = entity
        self._id = entity_id

    @property
    def message(self) -> str:
        if not self._id:
            return f"{self._entity} not found"
        return f"{self._entity} with id {self._id} not found"


class ConflictError(ApplicationError):
    pass


class UserAlreadyRelatedToShopError(ConflictError):
    @property
    def message(self) -> str:
        return "User already related to another shop"


class AlreadyExistsError(ConflictError):
    def __init__(self, entity: str) -> None:
        self._entity = entity

    @property
    def message(self) -> str:
        return f"{self._entity} already exists"


class ValidationError(ApplicationError):
    pass


class FieldError(ValidationError):
    def __init__(
        self, field: str, value: str, acceptable_values: list[Any]
    ) -> None:
        self._field = field
        self._value = value
        self._acceptable_values = acceptable_values

    @property
    def message(self) -> str:
        acceptable_values = ", ".join(self._acceptable_values)
        return (
            f"{self._field} cannot be {self._value}, use: {acceptable_values}"
        )


@dataclass(frozen=True)
class ExistingClientInfo:
    client_id: ClientId
    full_name: str


@dataclass(frozen=True)
class PhoneDuplicate:
    phone_number: str
    existing_clients: list[ExistingClientInfo]


class PhoneNumberAlreadyExistsError(ConflictError):
    def __init__(self, duplicates: list[PhoneDuplicate]) -> None:
        self._duplicates = duplicates

    @property
    def message(self) -> str:
        return "Phone number duplicates found"

    @property
    def duplicates(self) -> list[PhoneDuplicate]:
        return self._duplicates


class InvalidPrimaryFlagError(ValidationError):
    def __init__(self, field: str, count: int) -> None:
        self._field = field
        self._count = count

    @property
    def message(self) -> str:
        if self._count == 0:
            return f"Exactly one {self._field} must be marked as primary"
        return (
            f"Only one {self._field} can be marked as primary, "
            f"but {self._count} were provided"
        )


class DateMustBeGreaterThanError(ValidationError):
    def __init__(self, greater_than: date) -> None:
        self._greater_than = greater_than

    @property
    def message(self) -> str:
        return f"Date must be greater than {self._greater_than}"


class ProductIdRequiredForNewItemError(ValidationError):
    @property
    def message(self) -> str:
        return "product_id is required for new items (items without id)"


class LastTimeSlotError(ConflictError):
    @property
    def message(self) -> str:
        return (
            "Cannot delete the last time slot. "
            "Shop must have at least one time slot"
        )


class InvalidTimeSlotRangeError(ValidationError):
    @property
    def message(self) -> str:
        return "end_time must be greater than start_time"


class InvalidPhoneNumberError(ValidationError):
    def __init__(self, phone: str, reason: str) -> None:
        self._phone = phone
        self._reason = reason

    @property
    def message(self) -> str:
        return f"Invalid phone number '{self._phone}': {self._reason}"
