from dataclasses import dataclass

from delivery_service.shared.application.errors import NotFoundError


@dataclass(eq=False)
class ShopNotFoundError(NotFoundError):
    @property
    def message(self) -> str:
        return "Shop not found"
