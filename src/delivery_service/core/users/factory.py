from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from delivery_service.core.users.service_client import (
    ServiceClient,
)


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class ServiceClientFactory(Protocol):
    @abstractmethod
    def create_service_user(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData | None,
    ) -> ServiceClient: ...
