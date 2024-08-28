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
from domain.user.entity.user import User
from domain.user.value_objects.user_id import UserId
from infrastructure.gateways.converters import (
    convert_db_user_to_user_entity,
    convert_user_entity_to_db_user
)
from infrastructure.persistence.models import UserORM


class InMemoryUserGateway(UserReader, UserSaver):
    def __init__(self):
        self.users = {}

    def _get_from_memory(self, user_id: UserId) -> User | None:
        return self.users.get(user_id.to_raw())

    async def save(self, user: User) -> None:
        user_in_memory = self._get_from_memory(user.user_id)

        if user_in_memory:
            raise UserAlreadyExistsError(user.user_id.to_raw())

        self.users[user.user_id.to_raw()] = user

    async def by_id(self, user_id: UserId) -> User | None:
        return self._get_from_memory(user_id)

    async def update(self, user: User) -> None:
        self.users[user.user_id.to_raw()] = user

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
        db_user = convert_user_entity_to_db_user(user)

        self.session.add(db_user)
        try:
            await self.session.flush((db_user,))
        except IntegrityError as err:
            raise UserAlreadyExistsError(user.user_id.to_raw()) from err

    async def by_id(self, user_id: UserId) -> User | None:
        query = select(UserORM).where(UserORM.user_id == user_id.to_raw())

        result = await self.session.execute(query)

        db_user: UserORM | None = result.scalar()

        return None if not db_user else convert_db_user_to_user_entity(db_user)

    async def all(
            self,
            filters: GetUsersFilters,
            pagination: Pagination
    ) -> list[User]:
        query = select(UserORM)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(UserORM.created_at.asc())
        else:
            query = query.order_by(UserORM.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.offset(pagination.limit)

        if filters.roles is not None and filters.roles:
            query = query.where(UserORM.role.in_(filters.roles))

        result: Iterable[UserORM] = await self.session.scalars(query)

        return [convert_db_user_to_user_entity(db_user) for db_user in result]

    async def total_users(
            self,
            filters: GetUsersFilters
    ):
        query = select(func.count(UserORM.user_id))

        if filters.roles is not None and filters.roles:
            query = query.where(UserORM.role.in_(filters.roles))

        total: int = await self.session.scalar(query)

        return total

    async def update(self, user: User) -> None:
        db_user = convert_user_entity_to_db_user(user)

        try:
            await self.session.merge(db_user)
        except IntegrityError as err:
            raise GatewayError from err
