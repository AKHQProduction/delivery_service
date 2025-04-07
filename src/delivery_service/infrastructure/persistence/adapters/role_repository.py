from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.staff.role_repository import RoleRepository
from delivery_service.domain.staff.staff_role import Role, StaffRole
from delivery_service.infrastructure.persistence.tables.users import (
    ROLES_TABLE,
)


class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_name(self, name: Role) -> StaffRole | None:
        query = select(StaffRole).where(and_(ROLES_TABLE.c.name == name))

        result = await self._session.execute(query)
        return result.scalar_one_or_none()
