import uuid
from dataclasses import dataclass

from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.users.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
)
from delivery_service.core.users.service_client import (
    ServiceClient,
    ServiceClientID,
)


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class ServiceClientFactory:
    MIN_FULLNAME_LENGTH = 1
    MAX_FULLNAME_LENGTH = 128

    def create_service_user(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData | None,
    ) -> ServiceClient:
        self._validate(full_name)

        service_client_id = ServiceClientID(uuid.uuid4())

        service_client = ServiceClient(
            entity_id=service_client_id,
            full_name=full_name,
            telegram_contacts=self._set_telegram_contacts(
                data=telegram_contacts_data
            ),
        )

        return service_client

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
        if len(full_name) < self.MIN_FULLNAME_LENGTH:
            raise InvalidFullNameError()
        if len(full_name) > self.MAX_FULLNAME_LENGTH:
            raise FullNameTooLongError()
