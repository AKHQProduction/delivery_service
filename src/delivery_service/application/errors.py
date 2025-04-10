from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationError(Exception):
    @property
    def message(self) -> str:
        return "Application error"


@dataclass(eq=False)
class EntityAlreadyExistsError(ApplicationError):
    @property
    def message(self) -> str:
        return "Entity already exists"


@dataclass(eq=False)
class StaffMemberAlreadyExistsError(EntityAlreadyExistsError):
    pass


@dataclass(eq=False)
class ServiceUserAlreadyExistsError(EntityAlreadyExistsError):
    pass


@dataclass(eq=False)
class NotFoundError(ApplicationError):
    @property
    def message(self) -> str:
        return "Entity not found"


@dataclass(eq=False)
class ShopNotFoundError(NotFoundError):
    pass


@dataclass(eq=False)
class EmployeeNotFoundError(NotFoundError):
    pass


@dataclass(eq=False)
class ProductNotFoundError(NotFoundError):
    pass


@dataclass(eq=False)
class AuthenticationError(ApplicationError):
    pass
