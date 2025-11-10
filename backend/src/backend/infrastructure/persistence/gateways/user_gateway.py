from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces import CreateUserViaTgDTO, UserGateway
from backend.application.vars import UserId
from backend.infrastructure.persistence.tables import TelegramAccount, User


class SQLAlchemyUserGateway(UserGateway):
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

    def next_id(self) -> UserId:
        return UserId(UUID(str(uuid7())))
