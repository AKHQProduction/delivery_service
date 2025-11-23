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
