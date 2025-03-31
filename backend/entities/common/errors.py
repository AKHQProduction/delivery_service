from dataclasses import dataclass


@dataclass(eq=False)
class DomainError(Exception):
    @property
    def message(self):
        return "Application error"


@dataclass(eq=False)
class InvalidPriceError(DomainError):
    @property
    def message(self):
        return "Price must be greater than 0"


@dataclass(eq=False)
class InvalidQuantityError(DomainError):
    @property
    def message(self):
        return "Quantity must be greater than 0"
