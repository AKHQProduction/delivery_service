from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.dto import Pagination, SortOrder
from application.user.gateways.user import (
    GetUsersFilters,
    UserSaver,
    UserReader
)
from application.errors.gateway import GatewayError
from application.user.errors.user import UserAlreadyExistsError
from domain.user.entity.user import User, UserId
from infrastructure.persistence.models.user import users_table


class InMemoryUserGateway(UserReader, UserSaver):
    def __init__(self):
        self.users = {}

    def _get_from_memory(self, user_id: UserId) -> User | None:
        return self.users.get(user_id)

    async def save(self, user: User) -> None:
        user_in_memory = self._get_from_memory(user.user_id)

        if user_in_memory:
            raise UserAlreadyExistsError(user.user_id.to_raw())

        self.users[user.user_id] = user

    async def by_id(self, user_id: UserId) -> User | None:
        return self._get_from_memory(user_id)

    async def update(self, user: User) -> None:
        self.users[user.user_id] = user

    # TODO: implementation
    async def all(
            self,
            filters: GetUsersFilters,
            pagination: Pagination
    ) -> list[User]:
        pass

    async def total_users(
            self,
            filters: GetUsersFilters
    ):
        pass


class PostgreUserGateway(UserReader, UserSaver):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, user: User) -> None:
        try:
            self.session.add(user)
        except IntegrityError as err:
            raise UserAlreadyExistsError(user.user_id) from err

    async def by_id(self, user_id: UserId) -> User | None:
        query = select(User).where(users_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def all(
            self,
            filters: GetUsersFilters,
            pagination: Pagination
    ) -> list[User]:
        pass

    async def total_users(
            self,
            filters: GetUsersFilters
    ):
        pass
