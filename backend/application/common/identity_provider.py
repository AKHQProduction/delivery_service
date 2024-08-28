from abc import abstractmethod
from asyncio import Protocol

from domain.user.entity.user import RoleName, User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_user_role(self) -> RoleName:
        raise NotImplementedError
