from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces import CreateUserViaTgDTO
from backend.application.vars import UserId
from backend.infrastructure.persistence.tables import TelegramAccount, User


class SQLAlchemyUserGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
        self._session.add(
            User(
                id=data.user_id,
                telegram_account=TelegramAccount(
                    telegram_id=data.tg_id, full_name=data.full_name
                ),
            )
        )

    async def user_id_by_telegram_id(self, telegram_id: int) -> UserId | None:
        query = (
            select(User.id)
            .join(TelegramAccount)
            .where(TelegramAccount.telegram_id == telegram_id)
        )

        result = await self._session.execute(query)
        user_id = result.scalar()
        return UserId(user_id) if user_id else None

    def next_id(self) -> UserId:
        return UserId(UUID(str(uuid7())))
