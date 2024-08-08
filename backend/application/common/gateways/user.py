from abc import abstractmethod
from typing import Protocol

from backend.application.dto import UserDTO
from backend.domain.entities.user import User
from backend.domain.value_objects.user_id import UserId


class UserReader(Protocol):
    @abstractmethod
    async def by_id(self, user_id: UserId) -> User | None: ...


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: User) -> UserDTO: ...
