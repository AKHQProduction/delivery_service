from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.dto import Pagination, SortOrder
from application.user.gateway import (
    GetUsersFilters,
    UserSaver,
    UserReader
)
from application.user.errors import UserAlreadyExistsError
from entities.user.model import User, UserId
from infrastructure.persistence.models.user import users_table


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
        query = select(User)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(users_table.c.created_at.asc())
        else:
            query = query.order_by(users_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.offset(pagination.limit)

        if filters.roles is not None and filters.roles:
            query = query.where(users_table.c.role.in_(filters.roles))

        result = await self.session.scalars(query)

        return list(result.all())

    async def total_users(
            self,
            filters: GetUsersFilters
    ) -> int:
        query = select(func.count(users_table.c.user_id))

        if filters.roles is not None and filters.roles:
            query = query.where(users_table.c.role.in_(filters.roles))

        total: int = await self.session.scalar(query)

        return total
