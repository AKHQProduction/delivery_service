from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.domain.staff.role_repository import RoleRepository
from delivery_service.domain.staff.staff_role import Role, StaffRole
from delivery_service.infrastructure.persistence.tables.users import (
    ROLES_TABLE,
)


class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def load_with_names(self, names: list[Role]) -> Sequence[StaffRole]:
        query = select(StaffRole).where(ROLES_TABLE.c.name.in_(names))

        result = await self._session.execute(query)
        return result.scalars().all()
