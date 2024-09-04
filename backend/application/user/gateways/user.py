from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from application.common.dto import Pagination
from domain.user.entity.user import RoleName, User, UserId


@dataclass(frozen=True)
class GetUsersFilters:
    roles: list[RoleName] | None = None


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
    ):
        raise NotImplementedError


class UserSaver(Protocol):
    @abstractmethod
    async def save(self, user: User) -> None:
        raise NotImplementedError
