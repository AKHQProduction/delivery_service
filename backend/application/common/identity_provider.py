from abc import abstractmethod
from asyncio import Protocol

from entities.employee.models import EmployeeRole
from entities.user.models import User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_user(self) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_role(self) -> EmployeeRole | None:
        raise NotImplementedError
