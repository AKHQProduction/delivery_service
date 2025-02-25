from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from delivery_service.core.users.user import (
    User,
)


@dataclass(frozen=True)
class TelegramContactsData:
    telegram_id: int
    telegram_username: str | None


class UserFactory(Protocol):
    @abstractmethod
    async def create_user(
        self,
        full_name: str,
        telegram_contacts_data: TelegramContactsData,
    ) -> User: ...
