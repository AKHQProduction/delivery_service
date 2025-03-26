from dataclasses import dataclass

from delivery_service.shared.domain.errors import DomainError


@dataclass(eq=False)
class ApplicationError(Exception):
    @property
    def message(self) -> str:
        return "Application error"


@dataclass(eq=False)
class NotFoundError(ApplicationError):
    @property
    def message(self) -> str:
        return "Entity not found"


@dataclass(eq=False)
class EntityAlreadyExistsError(DomainError):
    @property
    def message(self) -> str:
        return "Entity already exists"
