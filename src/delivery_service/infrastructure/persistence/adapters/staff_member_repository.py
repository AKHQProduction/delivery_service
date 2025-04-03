from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.staff.repository import (
    StaffMemberRepository,
    TelegramContactsData,
)
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.infrastructure.persistence.tables.users import (
    SOCIAL_NETWORKS_TABLE,
)


class SQLAlchemyStaffMemberRepository(StaffMemberRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, staff_member: StaffMember) -> None:
        self._session.add(staff_member)

    async def exists(self, telegram_data: TelegramContactsData) -> bool:
        query = select(
            exists().where(
                and_(
                    SOCIAL_NETWORKS_TABLE.c.telegram_id
                    == telegram_data.telegram_id
                )
            )
        )

        result = await self._session.execute(query)
        return bool(result.scalar())

    async def load_with_telegram_id(
        self, telegram_id: int
    ) -> StaffMember | None:
        query = select(StaffMember).where(
            and_(SOCIAL_NETWORKS_TABLE.c.telegram_id == telegram_id)
        )

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
