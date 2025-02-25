from typing import Final

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.users.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
    UserAlreadyExistsError,
)
from delivery_service.core.users.factory import (
    TelegramContactsData,
    UserFactory,
)
from delivery_service.core.users.repository import UserRepository
from delivery_service.core.users.user import User


class UserFactoryImpl(UserFactory):
    _MIN_FULLNAME_LENGTH: Final[int] = 1
    _MAX_FULLNAME_LENGTH: Final[int] = 128

    def __init__(
        self, id_generator: IDGenerator, user_repository: UserRepository
    ) -> None:
        self._id_generator = id_generator
        self._user_repository = user_repository

    async def create_user(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData,
    ) -> User:
        self._validate(full_name)

        if not await self._user_repository.exists(
            telegram_data=telegram_contacts_data
        ):
            return User(
                entity_id=self._id_generator.generate_service_client_id(),
                full_name=full_name,
                telegram_contacts=TelegramContacts(
                    telegram_id=telegram_contacts_data.telegram_id,
                    telegram_username=telegram_contacts_data.telegram_username,
                ),
            )
        raise UserAlreadyExistsError(
            telegram_id=telegram_contacts_data.telegram_id
        )

    def _validate(self, full_name: str) -> None:
        if len(full_name) < self._MIN_FULLNAME_LENGTH:
            raise InvalidFullNameError()
        if len(full_name) > self._MAX_FULLNAME_LENGTH:
            raise FullNameTooLongError()
