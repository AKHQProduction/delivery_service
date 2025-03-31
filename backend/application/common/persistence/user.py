from abc import abstractmethod
from asyncio import Protocol

from application.common.persistence.view_models import UserView
from entities.user.models import User, UserId


class UserGateway(Protocol):
    @abstractmethod
    async def load_with_id(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def load_with_tg_id(self, tg_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def is_exists(self, phone_number: str) -> bool:
        raise NotImplementedError


class UserReader(Protocol):
    @abstractmethod
    async def read_profile_with_tg_id(self, tg_id: int) -> UserView | None:
        raise NotImplementedError
