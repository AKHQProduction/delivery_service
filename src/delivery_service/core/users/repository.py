from abc import abstractmethod
from typing import Protocol

from delivery_service.core.users.factory import TelegramContactsData
from delivery_service.core.users.user import User


class UserRepository(Protocol):
    @abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, telegram_data: TelegramContactsData) -> bool:
        raise NotImplementedError
