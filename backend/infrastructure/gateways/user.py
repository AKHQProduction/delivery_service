from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.gateways.user import UserSaver, UserReader
from application.dto import UserDTO
from application.errors.user import UserAlreadyExistsError
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from infrastructure.persistence.models import UserORM


class InMemoryUserGateway(UserReader, UserSaver):
    def __init__(self):
        self.users = {}

    def _get_from_memory(self, user_id: UserId) -> User | None:
        return self.users.get(user_id.to_raw())

    async def save(self, user: User) -> UserDTO:
        user_in_memory = self._get_from_memory(user.user_id)

        if user_in_memory:
            raise UserAlreadyExistsError(user.user_id.to_raw())

        self.users[user.user_id.to_raw()] = user

        return UserDTO(
                user_id=user.user_id.to_raw(),
                full_name=user.full_name,
                username=user.username,
                phone_number=user.phone_number
        )

    async def by_id(self, user_id: UserId) -> User | None:
        return self._get_from_memory(user_id)


class PostgreUserGateway(UserReader, UserSaver):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, user: User) -> UserDTO:
        db_user = UserORM(
                user_id=user.user_id.to_raw(),
                full_name=user.full_name,
                username=user.username,
        )

        try:
            await self.session.merge(db_user)
        except IntegrityError as err:
            raise UserAlreadyExistsError(user.user_id.to_raw()) from err

        return UserDTO(
                user_id=db_user.user_id,
                full_name=db_user.full_name,
                username=db_user.username,
                phone_number=db_user.phone_number
        )

    async def by_id(self, user_id: UserId) -> User | None:
        query = select(UserORM).where(UserORM.user_id == user_id.to_raw())

        result = await self.session.execute(query)

        user: UserORM | None = result.scalar()

        return None if not user else User(
                user_id=UserId(user.user_id),
                full_name=user.full_name,
                username=user.username,
                phone_number=user.phone_number,
                role=user.role,
                is_active=user.is_active,
        )
