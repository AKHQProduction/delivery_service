from dataclasses import dataclass

from delivery_service.shared.application.errors import NotFoundError


@dataclass(eq=False)
class ShopNotFoundError(NotFoundError):
    @property
    def message(self) -> str:
        return "Shop not found"


@dataclass(eq=False)
class EmployeeNotFoundError(NotFoundError):
    @property
    def message(self) -> str:
        return "Employee not found error"
