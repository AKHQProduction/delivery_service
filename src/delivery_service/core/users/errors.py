from dataclasses import dataclass

from delivery_service.core.shared.errors import ValidationError


@dataclass(eq=False)
class InvalidFullNameError(ValidationError):
    @property
    def message(self) -> str:
        return "Invalid full name length"


@dataclass(eq=False)
class FullNameTooLongError(ValidationError):
    @property
    def message(self) -> str:
        return "Full name cannot exceed 128 characters"


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
