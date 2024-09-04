from dataclasses import dataclass

from domain.common.errors.base import DomainError


@dataclass(eq=False)
class InvalidBotTokenError(DomainError):
    token: str

    @property
    def message(self):
        return f"Invalid bot token {self.token}"


@dataclass(eq=False)
class ShopTitleTooShortError(DomainError):
    title: str

    @property
    def message(self):
        return f"Shop title is too short, value - {self.title}"


@dataclass(eq=False)
class ShopTitleTooLongError(DomainError):
    title: str

    @property
    def message(self):
        return f"Shop title is too long, value - {self.title}"
