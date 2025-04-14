from abc import abstractmethod
from typing import Protocol

from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.users.service_user import ServiceUser


class ServiceUserRepository(Protocol):
    @abstractmethod
    def add(self, service_user: ServiceUser) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, telegram_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_with_social_network(
        self, telegram_id: int
    ) -> ServiceUser | None:
        raise NotImplementedError

    @abstractmethod
    async def load_by_identity(self, user_id: UserID) -> ServiceUser | None:
        raise NotImplementedError
