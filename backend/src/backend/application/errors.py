from typing import Any


class ApplicationError(Exception):
    """Base application error."""


class AuthorizationError(ApplicationError):
    @property
    def message(self) -> str:
        return "User not authorization"


class UserAlreadyRelatedToShopError(ApplicationError):
    @property
    def message(self) -> str:
        return "User already related to another shop"


class AccessDeniedError(ApplicationError):
    @property
    def message(self) -> str:
        return "Access denied to this resource"


class EntityNotFoundError(ApplicationError):
    def __init__(self, entity: str) -> None:
        self._entity = entity

    @property
    def message(self) -> str:
        return f"{self._entity} not found"


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
        acceptable_values = " ,".join(self._acceptable_values)
        return f"{self._field} cant be {self._value}, use: {acceptable_values}"


class PhoneNumberAlreadyExistsError(ApplicationError):
    def __init__(self, phone_number: str) -> None:
        self._phone_number = phone_number

    @property
    def message(self) -> str:
        return (
            f"Phone number {self._phone_number} is already used "
            "by another client"
        )


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
