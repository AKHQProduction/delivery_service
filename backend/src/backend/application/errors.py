class ApplicationError(Exception):
    """Base application error."""


class AuthorizationError(Exception):
    @property
    def message(self) -> str:
        return "User not authorization"


class UserAlreadyRelatedToShopError(Exception):
    @property
    def message(self) -> str:
        return "User already related to another shop"


class AccessDeniedError(Exception):
    @property
    def message(self) -> str:
        return "Access denied to this resource"


class EntityNotFoundError(Exception):
    def __init__(self, entity: str) -> None:
        self._entity = entity

    @property
    def message(self) -> str:
        return f"{self._entity} not found"
