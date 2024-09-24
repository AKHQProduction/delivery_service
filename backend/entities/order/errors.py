from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class InvalidOrderItemQuantityError(DomainError):
    @property
    def message(self):
        return "Quantity must be grate than 0"
