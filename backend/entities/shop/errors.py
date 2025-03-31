from dataclasses import dataclass

from entities.common.errors import DomainError


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


@dataclass(eq=False)
class InvalidRegularDayOffError(DomainError):
    @property
    def message(self):
        return "The day must be between 0 and 6"


@dataclass(eq=False)
class InvalidSpecialDayOffError(DomainError):
    @property
    def message(self):
        return "The date must be in the future"


@dataclass(eq=False)
class InvalidDeliveryDistanceError(DomainError):
    @property
    def message(self):
        return "You need to specify a longer distance for delivery"
