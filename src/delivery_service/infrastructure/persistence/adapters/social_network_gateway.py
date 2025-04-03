from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables import USERS_TABLE
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
            and_(SOCIAL_NETWORKS_TABLE.c.user_id == user_id)
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_telegram_data(
        self, offset: int = 0, limit: int = 100
    ) -> dict[int, TelegramData]:
        query = (
            select(
                SOCIAL_NETWORKS_TABLE.c.user_id.label("user_id"),
                SOCIAL_NETWORKS_TABLE.c.telegram_id.label("tg_id"),
                SOCIAL_NETWORKS_TABLE.c.telegram_username.label("username"),
                USERS_TABLE.c.full_name.label("full_name"),
            )
            .join(
                USERS_TABLE,
                and_(USERS_TABLE.c.id == SOCIAL_NETWORKS_TABLE.c.user_id),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(query)

        return {
            row.tg_id: TelegramData(
                row_id=row.user_id,
                full_name=row.full_name,
                username=row.username,
            )
            for row in result.mappings()
        }

    async def total(self) -> int:
        query = select(func.count(SOCIAL_NETWORKS_TABLE.c.user_id))

        total: int = (await self._session.scalar(query)) or 0
        return total

    async def update_data(
        self, data_to_update: dict[UUID, dict[str, Any]]
    ) -> None:
        update_username = case(
            *[
                (
                    SOCIAL_NETWORKS_TABLE.c.user_id == user_id,
                    values["username"],
                )
                for user_id, values in data_to_update.items()
            ],
            else_=SOCIAL_NETWORKS_TABLE.c.telegram_username,
        )

        stmt_social = (
            update(SOCIAL_NETWORKS_TABLE)
            .where(SOCIAL_NETWORKS_TABLE.c.user_id.in_(data_to_update.keys()))
            .values(telegram_username=update_username)
        )

        update_full_name = case(
            *[
                (USERS_TABLE.c.id == user_id, values["full_name"])
                for user_id, values in data_to_update.items()
            ],
            else_=USERS_TABLE.c.full_name,
        )

        stmt_users = (
            update(USERS_TABLE)
            .where(USERS_TABLE.c.id.in_(data_to_update.keys()))
            .values(full_name=update_full_name)
        )

        await self._session.execute(stmt_social)
        await self._session.execute(stmt_users)
