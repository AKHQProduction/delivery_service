from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid_utils.compat import uuid7

from backend.application.vars import UserId
from backend.infrastructure.persistence.tables import TelegramAccount, User


class SQLAlchemyUserGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def save(self, user: User) -> None:
        self._session.add(user)

    async def user_id_by_telegram_id(self, telegram_id: int) -> UserId | None:
        query = (
            select(User.id)
            .join(TelegramAccount)
            .where(TelegramAccount.telegram_id == telegram_id)
        )

        result = await self._session.execute(query)
        user_id = result.scalar()
        return UserId(user_id) if user_id else None

    async def load_user_with_tg(self, user_id: UserId) -> User | None:
        query = (
            select(User)
            .options(joinedload(User.telegram_account))
            .where(User.id == user_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    def next_id(self) -> UserId:
        return UserId(uuid7())
