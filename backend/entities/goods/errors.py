from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class GoodsTitleTooShortError(DomainError):
    title: str

    @property
    def message(self):
        return f"Goods title={self.title} is too short"


@dataclass(eq=False)
class GoodsTitleTooLongError(DomainError):
    title: str

    @property
    def message(self):
        return f"Goods title={self.title} is too long"


@dataclass(eq=False)
class InvalidGoodsPriceError(DomainError):
    @property
    def message(self):
        return "Goods price must be greater than 0"
