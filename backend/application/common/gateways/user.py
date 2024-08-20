from abc import abstractmethod
from typing import Protocol

from application.dto import UserDTO
from domain.entities.user import User
from domain.value_objects.user_id import UserId


class UserReader(Protocol):
    @abstractmethod
    async def by_id(self, user_id: UserId) -> User | None:
        raise NotImplementedError


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: User) -> UserDTO:
        raise NotImplementedError
