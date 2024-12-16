from sqlalchemy import RowMapping, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.persistence.user import (
    UserGateway,
    UserReader,
    UserView,
)
from application.common.persistence.view_models import UserAddress
from entities.user.models import User, UserId
from entities.user.value_objects import PhoneNumber
from infrastructure.persistence.models.user import users_table


class SQLAlchemyUserMapper(UserGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def load_with_id(self, user_id: UserId) -> User | None:
        return await self.session.get(User, user_id)

    async def load_with_tg_id(self, tg_id: int) -> User | None:
        query = select(User).where(users_table.c.tg_id == tg_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def is_exists(self, phone_number: PhoneNumber) -> bool:
        query = select(exists()).where(
            users_table.c.phone_number == phone_number
        )

        result = await self.session.execute(query)

        return result.scalar()


class SQLAlchemyUserReader(UserReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    @staticmethod
    def _load_user_profile(row: RowMapping) -> UserView:
        return UserView(
            user_id=row.user_id,
            full_name=row.full_name,
            username=row.username,
            tg_id=row.tg_id,
            phone_number=row.phone_number,
            address=UserAddress(
                city=row.address_city,
                street=row.address_street,
                house_number=row.address_house_number,
            ),
        )

    async def read_profile_with_tg_id(self, tg_id: int) -> UserView | None:
        query = select(
            users_table.c.user_id,
            users_table.c.full_name,
            users_table.c.username,
            users_table.c.tg_id,
            users_table.c.phone_number,
            users_table.c.address_city,
            users_table.c.address_street,
            users_table.c.address_house_number,
        ).where(users_table.c.tg_id == tg_id)

        result = await self.session.execute(query)

        row = result.mappings().one_or_none()

        return None if not row else self._load_user_profile(row)
