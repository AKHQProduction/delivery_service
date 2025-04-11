from typing import Sequence

from sqlalchemy import RowMapping, Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.query.ports.staff_gateway import (
    StaffGatewayFilters,
    StaffMemberGateway,
    StaffReadModel,
)
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.persistence.tables import USERS_TABLE
from delivery_service.infrastructure.persistence.tables.shops import (
    STAFF_MEMBERS_TABLE,
)
from delivery_service.infrastructure.persistence.tables.users import (
    ROLES_TABLE,
    USERS_TO_ROLES_TABLE,
)


class SQLAlchemyStaffMemberGateway(StaffMemberGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _set_filters(query: Select, filters: StaffGatewayFilters) -> Select:
        if filters.shop_id is not None:
            query = query.where(
                and_(STAFF_MEMBERS_TABLE.c.shop_id == filters.shop_id)
            )

        return query

    @staticmethod
    def _map_row_to_read_model(row: RowMapping) -> StaffReadModel:
        roles = [role for role in row.roles if role is not None]
        return StaffReadModel(
            staff_id=row.staff_id, full_name=row.full_name, roles=roles
        )

    @staticmethod
    def _select_rows() -> Select:
        return (
            select(
                USERS_TABLE.c.id.label("staff_id"),
                USERS_TABLE.c.full_name,
                func.array_agg(ROLES_TABLE.c.name).label("roles"),
            )
            .select_from(
                USERS_TABLE.join(
                    STAFF_MEMBERS_TABLE,
                    USERS_TABLE.c.id == STAFF_MEMBERS_TABLE.c.user_id,
                )
                .outerjoin(
                    USERS_TO_ROLES_TABLE,
                    USERS_TABLE.c.id == USERS_TO_ROLES_TABLE.c.user_id,
                )
                .outerjoin(
                    ROLES_TABLE,
                    USERS_TO_ROLES_TABLE.c.role_id == ROLES_TABLE.c.id,
                )
            )
            .group_by(USERS_TABLE.c.id, USERS_TABLE.c.full_name)
        )

    async def read_staff_member(
        self, user_id: UserID
    ) -> StaffReadModel | None:
        query = self._select_rows()
        query = query.where(and_(STAFF_MEMBERS_TABLE.c.user_id == user_id))

        result = await self._session.execute(query)
        row = result.mappings().one_or_none()

        return self._map_row_to_read_model(row) if row else None

    async def read_all_staff(
        self, filters: StaffGatewayFilters | None = None
    ) -> Sequence[StaffReadModel]:
        query = self._select_rows()

        if filters:
            query = self._set_filters(query, filters)

        result = await self._session.execute(query)

        return [self._map_row_to_read_model(row) for row in result.mappings()]

    async def total(self, filters: StaffGatewayFilters | None = None) -> int:
        query = select(func.count(STAFF_MEMBERS_TABLE.c.user_id))

        if filters:
            query = self._set_filters(query=query, filters=filters)

        result = await self._session.execute(query)
        return result.scalar_one()
