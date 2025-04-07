from typing import Final

from delivery_service.application.common.dto import TelegramContactsData
from delivery_service.application.errors import ServiceUserAlreadyExistsError
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.shared.vo.tg_contacts import TelegramContacts
from delivery_service.domain.staff.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
)
from delivery_service.domain.user.repository import ServiceUserRepository
from delivery_service.domain.user.service_user import ServiceUser


class ServiceUserFactory:
    _MIN_FULLNAME_LENGTH: Final[int] = 1
    _MAX_FULLNAME_LENGTH: Final[int] = 128

    def __init__(
        self, repository: ServiceUserRepository, id_generator: IDGenerator
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator

    async def create_service_user(
        self, full_name: str, telegram_contacts: TelegramContactsData
    ) -> ServiceUser:
        self._validate(full_name)

        if not await self._repository.exists(telegram_contacts.telegram_id):
            user_id = self._id_generator.generate_user_id()
            return ServiceUser(
                entity_id=user_id,
                full_name=full_name,
                telegram_contacts=TelegramContacts(
                    _user_id=user_id,
                    telegram_id=telegram_contacts.telegram_id,
                    telegram_username=telegram_contacts.telegram_username,
                ),
            )
        raise ServiceUserAlreadyExistsError()

    def _validate(self, full_name: str) -> None:
        if len(full_name) < self._MIN_FULLNAME_LENGTH:
            raise InvalidFullNameError()
        if len(full_name) > self._MAX_FULLNAME_LENGTH:
            raise FullNameTooLongError()
