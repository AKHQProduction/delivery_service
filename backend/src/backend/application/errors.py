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
