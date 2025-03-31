from dataclasses import dataclass

from delivery_service.domain.shared.errors import ConflictError


@dataclass(eq=False)
class ProductAlreadyExistsError(ConflictError):
    @property
    def message(self) -> str:
        return "Product already exists"


@dataclass(eq=False)
class AccessDeniedError(ConflictError):
    @property
    def message(self) -> str:
        return "Access denied"
