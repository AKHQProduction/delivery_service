from dataclasses import dataclass

from delivery_service.domain.shared.errors import (
    InvalidTelegramUsernameError,
    TelegramIDMustBePositiveError,
)

MIN_TELEGRAM_ID_VALUE = 1
MIN_TELEGRAM_USERNAME_LENGTH = 1
MAX_TELEGRAM_USERNAME_LENGTH = 128


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class TelegramContacts:
    telegram_id: int
    telegram_username: str | None = None

    def __post_init__(self) -> None:
        if self.telegram_id < MIN_TELEGRAM_ID_VALUE:
            raise TelegramIDMustBePositiveError()

        if self.telegram_username is not None:
            username_length = len(self.telegram_username)
            if not (
                MIN_TELEGRAM_USERNAME_LENGTH
                <= username_length
                <= MAX_TELEGRAM_USERNAME_LENGTH
            ):
                raise InvalidTelegramUsernameError()

    def __str__(self) -> str:
        return (
            f"<TGContacts: telegram ID - {self.telegram_id}, "
            f"username - {self.telegram_username}>"
        )
