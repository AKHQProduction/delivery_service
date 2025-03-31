from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class InvalidOrderItemQuantityError(DomainError):
    @property
    def message(self):
        return "Quantity must be grate than 0"


@dataclass(eq=False)
class InvalidOrderTotalPriceError(DomainError):
    @property
    def message(self):
        return "Quantity must be positive number"


@dataclass(eq=False)
class InvalidBottlesQuantityError(DomainError):
    @property
    def message(self):
        return "Quantity bottles to exchange must be greate"
