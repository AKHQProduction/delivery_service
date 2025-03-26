from dataclasses import dataclass


@dataclass(eq=False)
class DomainError(Exception):
    @property
    def message(self) -> str:
        return "Domain error"


@dataclass(eq=False)
class ValidationError(DomainError):
    @property
    def message(self) -> str:
        return "Validation error"


@dataclass(eq=False)
class ConflictError(DomainError):
    @property
    def message(self) -> str:
        return "Conflict error"


@dataclass(eq=False)
class ValueMustBePositiveError(ConflictError):
    @property
    def message(self) -> str:
        return "Price must be greate than 0"


@dataclass(eq=False)
class TelegramIDMustBePositiveError(ValidationError):
    @property
    def message(self) -> str:
        return "Telegram id must be positive"


@dataclass(eq=False)
class InvalidTelegramUsernameError(ValidationError):
    @property
    def message(self) -> str:
        return (
            "Telegram username length must be greate than 0 and less than 129"
        )
