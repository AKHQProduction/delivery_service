from typing import Final

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.users.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
)
from delivery_service.core.users.factory import (
    TelegramContactsData,
    UserFactory,
)
from delivery_service.core.users.user import User


class UserFactoryImpl(UserFactory):
    _MIN_FULLNAME_LENGTH: Final[int] = 1
    _MAX_FULLNAME_LENGTH: Final[int] = 128

    def __init__(self, id_generator: IDGenerator) -> None:
        self._id_generator = id_generator

    def create_user(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData | None,
    ) -> User:
        self._validate(full_name)
        return User(
            entity_id=self._id_generator.generate_service_client_id(),
            full_name=full_name,
            telegram_contacts=self._set_telegram_contacts(
                telegram_contacts_data
            ),
        )

    @staticmethod
    def _set_telegram_contacts(
        data: TelegramContactsData | None,
    ) -> TelegramContacts | None:
        if data:
            return TelegramContacts(
                telegram_id=data.telegram_id,
                telegram_username=data.telegram_username,
            )
        return None

    def _validate(self, full_name: str) -> None:
        if len(full_name) < self._MIN_FULLNAME_LENGTH:
            raise InvalidFullNameError()
        if len(full_name) > self._MAX_FULLNAME_LENGTH:
            raise FullNameTooLongError()
