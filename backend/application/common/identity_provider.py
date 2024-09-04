from abc import abstractmethod
from asyncio import Protocol

from entities.user.models.user import RoleName, User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User:
        raise NotImplementedError
