from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from application.common.request_data import Pagination
from entities.user.models import User, UserId


@dataclass(frozen=True)
class GetUsersFilters:
    pass


class UserReader(Protocol):
    @abstractmethod
    async def by_id(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def all(
            self,
            filters: GetUsersFilters,
            pagination: Pagination
    ) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def total_users(
            self,
            filters: GetUsersFilters
    ) -> int:
        raise NotImplementedError


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: User) -> None:
        raise NotImplementedError
