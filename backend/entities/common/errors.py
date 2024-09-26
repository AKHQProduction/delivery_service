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
