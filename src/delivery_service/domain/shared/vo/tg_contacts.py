from dataclasses import dataclass

from delivery_service.domain.shared.dto import Empty
from delivery_service.domain.shared.errors import (
    InvalidTelegramUsernameError,
    TelegramIDMustBePositiveError,
)
from delivery_service.domain.shared.user_id import UserID

MIN_TELEGRAM_ID_VALUE = 1
MIN_TELEGRAM_USERNAME_LENGTH = 1
MAX_TELEGRAM_USERNAME_LENGTH = 128


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class TelegramContacts:
    _user_id: UserID
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

    def edit_contacts(
        self,
        telegram_id: int | None,
        telegram_username: str | None | Empty = Empty.UNSET,
    ) -> "TelegramContacts":
        if telegram_id is None or telegram_username is None:
            raise ValueError()

        if telegram_id is not None:
            self._edit_telegram_id(telegram_id)
        if telegram_username is not None:
            self._edit_telegram_username(telegram_username)

        return TelegramContacts(
            self._user_id,
            telegram_id=self.telegram_id,
            telegram_username=self.telegram_username,
        )

    def _edit_telegram_id(self, telegram_id: int) -> "TelegramContacts":
        return TelegramContacts(
            _user_id=self._user_id,
            telegram_id=telegram_id,
            telegram_username=self.telegram_username,
        )

    def _edit_telegram_username(
        self, telegram_username: str | Empty
    ) -> "TelegramContacts":
        new_username = (
            None if telegram_username is Empty.UNSET else telegram_username
        )

        return TelegramContacts(
            _user_id=self._user_id,
            telegram_id=self.telegram_id,
            telegram_username=new_username,
        )

    def __str__(self) -> str:
        return (
            f"<TGContacts: telegram ID - {self.telegram_id}, "
            f"username - {self.telegram_username}>"
        )
