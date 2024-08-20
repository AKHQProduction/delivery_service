from abc import abstractmethod
from asyncio import Protocol

from domain.entities.role import Role
from domain.entities.user import User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_roles(self) -> list[Role]:
        raise NotImplementedError
