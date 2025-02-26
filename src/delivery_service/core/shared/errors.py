from dataclasses import dataclass


@dataclass(eq=False)
class DomainError(Exception):
    @property
    def message(self) -> str:
        return "Domain error"


@dataclass(eq=False)
class ValidationError(DomainError):
    @property
    def message(self) -> str:
        return "Validation error"


@dataclass(eq=False)
class EntityAlreadyExistsError(DomainError):
    @property
    def message(self) -> str:
        return "Entity already exists"


@dataclass(eq=False)
class ConflictError(DomainError):
    @property
    def message(self) -> str:
        return "Conflict error"
