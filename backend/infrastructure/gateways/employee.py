from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.input_data import Pagination, SortOrder
from application.employee.errors import EmployeeAlreadyExistError
from application.employee.gateway import (
    EmployeeFilters,
    EmployeeReader,
    EmployeeSaver,
)
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId
from infrastructure.persistence.models.employee import employees_table


class EmployeeGateway(EmployeeSaver, EmployeeReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, employee: Employee) -> None:
        self.session.add(employee)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise EmployeeAlreadyExistError(employee.user_id) from error

    async def by_identity(self, user_id: UserId) -> Employee | None:
        query = select(Employee).where(employees_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete(self, employee_id: EmployeeId) -> None:
        query = delete(Employee).where(
            employees_table.c.employee_id == employee_id
        )

        await self.session.execute(query)

    async def all(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[Employee]:
        query = select(Employee)

        if filters and filters.shop_id:
            query = query.where(employees_table.c.shop_id == filters.shop_id)

        if pagination.order is SortOrder.ASC:
            query = query.order_by(employees_table.c.created_at.asc())
        else:
            query = query.order_by(employees_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.offset(pagination.limit)

        result = await self.session.scalars(query)

        return list(result.all())

    async def total(self, filters: EmployeeFilters) -> int:
        query = select(func.count(employees_table.c.employee_id))

        if filters and filters.shop_id:
            query = query.where(employees_table.c.shop_id == filters.shop_id)

        total: int = await self.session.scalar(query)

        return total
