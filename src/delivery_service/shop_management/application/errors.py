from dataclasses import dataclass

from delivery_service.shared.application.errors import NotFoundError


@dataclass(eq=False)
class ShopNotFoundError(NotFoundError):
    pass


@dataclass(eq=False)
class EmployeeNotFoundError(NotFoundError):
    pass
