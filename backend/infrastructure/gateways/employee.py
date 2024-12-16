from sqlalchemy import RowMapping, and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.persistence.employee import (
    EmployeeGateway,
    EmployeeReader,
    EmployeeReaderFilters,
)
from application.common.persistence.view_models import EmployeeView
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId
from infrastructure.persistence.models.employee import employees_table
from infrastructure.persistence.models.user import users_table


class SQLAlchemyEmployeeMapper(EmployeeGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def is_exist(self, user_id: UserId) -> bool:
        query = select(exists().where(employees_table.c.user_id == user_id))

        result = await self.session.execute(query)

        return result.scalar()

    async def load_with_identity(self, user_id: UserId) -> Employee | None:
        query = select(Employee).where(employees_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def load_with_id(self, employee_id: EmployeeId) -> Employee | None:
        return await self.session.get(Employee, employee_id)


class SQLAlchemyEmployeeReader(EmployeeReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_employee_card(row: RowMapping) -> EmployeeView:
        return EmployeeView(
            employee_id=row.employee_id,
            user_id=row.user_id,
            full_name=row.full_name,
            role=row.role,
        )

    async def read_many(
        self, filters: EmployeeReaderFilters | None = None
    ) -> list[EmployeeView]:
        query = select(
            employees_table.c.employee_id,
            employees_table.c.user_id,
            users_table.c.full_name,
            employees_table.c.role,
        ).join(
            users_table,
            and_(employees_table.c.user_id == users_table.c.user_id),
        )

        if filters and filters.shop_id:
            query = query.where(employees_table.c.shop_id == filters.shop_id)

        result = await self.session.execute(query)

        return [self._load_employee_card(row) for row in result.mappings()]

    async def read_with_id(
        self, employee_id: EmployeeId
    ) -> EmployeeView | None:
        query = (
            select(
                employees_table.c.employee_id,
                employees_table.c.user_id,
                users_table.c.full_name,
                employees_table.c.role,
            )
            .join(
                users_table,
                and_(employees_table.c.user_id == users_table.c.user_id),
            )
            .where(employees_table.c.employee_id == employee_id)
        )

        result = await self.session.execute(query)

        row = result.mappings().one_or_none()

        if not row:
            return None
        return self._load_employee_card(row)
