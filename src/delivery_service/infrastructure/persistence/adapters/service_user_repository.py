from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.user.repository import ServiceUserRepository
from delivery_service.domain.user.service_user import ServiceUser
from delivery_service.infrastructure.persistence.tables.users import (
    SOCIAL_NETWORKS_TABLE,
)


class SQLAlchemyServiceUserRepository(ServiceUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, service_user: ServiceUser) -> None:
        self._session.add(service_user)

    async def exists(self, telegram_id: int) -> bool:
        query = select(
            exists().where(
                and_(SOCIAL_NETWORKS_TABLE.c.telegram_id == telegram_id)
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())

    async def load_with_social_network(
        self, telegram_id: int
    ) -> ServiceUser | None:
        query = select(ServiceUser).where(
            and_(SOCIAL_NETWORKS_TABLE.c.telegram_id == telegram_id)
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
