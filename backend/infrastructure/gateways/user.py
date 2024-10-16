from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.input_data import Pagination, SortOrder
from application.user.errors import UserAlreadyExistError
from application.user.gateway import GetUsersFilters, UserReader, UserSaver
from entities.user.models import User, UserId
from infrastructure.persistence.models.user import users_table


class UserGateway(UserReader, UserSaver):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, user: User) -> None:
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise UserAlreadyExistError(user.user_id) from error

    async def by_id(self, user_id: UserId) -> User | None:
        query = select(User).where(users_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def all(
        self, filters: GetUsersFilters, pagination: Pagination
    ) -> list[User]:
        query = select(User)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(users_table.c.created_at.asc())
        else:
            query = query.order_by(users_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.limit(pagination.limit)

        result = await self.session.scalars(query)

        return list(result.all())

    async def total(self, filters: GetUsersFilters) -> int:
        query = select(func.count(users_table.c.user_id))

        total: int = await self.session.scalar(query)

        return total
