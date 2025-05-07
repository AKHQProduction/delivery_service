from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables.users import (
    SOCIAL_NETWORKS_TABLE,
)


@dataclass
class TelegramData:
    row_id: UUID
    full_name: str
    username: str | None


class SQlAlchemySocialNetworkGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_current_user_telegram_id(
        self, user_id: UserID
    ) -> int | None:
        query = select(SOCIAL_NETWORKS_TABLE.c.telegram_id).where(
            and_(SOCIAL_NETWORKS_TABLE.c.customer_id == user_id)
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
