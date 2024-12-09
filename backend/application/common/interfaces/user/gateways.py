from abc import abstractmethod
from asyncio import Protocol

from application.common.interfaces.user.read_models import UserProfile
from entities.user.models import User, UserId


class UserGateway(Protocol):
    @abstractmethod
    async def get_with_id(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_with_tg_id(self, tg_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def is_exists(self, phone_number: str) -> bool:
        raise NotImplementedError


class UserReader(Protocol):
    @abstractmethod
    async def get_profile_with_tg_id(self, tg_id: int) -> UserProfile | None:
        raise NotImplementedError
