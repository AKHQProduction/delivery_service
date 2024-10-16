from typing import Any

from sqlalchemy import Row, and_, delete, exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.input_data import Pagination, SortOrder
from application.employee.errors import EmployeeAlreadyExistError
from application.employee.gateway import (
    EmployeeFilters,
    EmployeeGateway,
    EmployeeReader,
)
from application.employee.output_data import EmployeeCard
from entities.employee.models import Employee, EmployeeId
from entities.user.models import UserId
from infrastructure.persistence.models.employee import employees_table
from infrastructure.persistence.models.user import users_table


def map_rows_to_employee_card(
    row: Row[tuple[Any, Any, Any, Any]],
) -> EmployeeCard:
    return EmployeeCard(
        employee_id=row.employee_id,
        user_id=row.user_id,
        full_name=row.full_name,
        role=row.role,
    )


class EmployeeMapper(EmployeeGateway, EmployeeReader):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, employee: Employee) -> None:
        self.session.add(employee)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise EmployeeAlreadyExistError(employee.user_id) from error

    async def is_exist(self, user_id: UserId) -> bool:
        query = select(exists().where(employees_table.c.user_id == user_id))

        result = await self.session.execute(query)

        return result.scalar()

    async def by_identity(self, user_id: UserId) -> Employee | None:
        query = select(Employee).where(employees_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def by_id(self, employee_id: EmployeeId) -> Employee | None:
        query = select(Employee).where(
            employees_table.c.employee_id == employee_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete(self, employee_id: EmployeeId) -> None:
        query = delete(Employee).where(
            employees_table.c.employee_id == employee_id
        )

        await self.session.execute(query)

    async def total(self, filters: EmployeeFilters) -> int:
        query = select(func.count(employees_table.c.employee_id))

        if filters and filters.shop_id:
            query = query.where(employees_table.c.shop_id == filters.shop_id)

        total: int = await self.session.scalar(query)

        return total

    async def all_cards(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[EmployeeCard]:
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

        if pagination.order is SortOrder.ASC:
            query = query.order_by(employees_table.c.created_at.asc())
        else:
            query = query.order_by(employees_table.c.created_at.desc())

        if pagination.offset is not None:
            query = query.offset(pagination.offset)
        if pagination.limit is not None:
            query = query.limit(pagination.limit)

        result = await self.session.execute(query)

        return [map_rows_to_employee_card(row) for row in result.fetchall()]

    async def card_by_id(self, employee_id: EmployeeId) -> EmployeeCard | None:
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

        row = result.fetchone()

        if not row:
            return None
        return map_rows_to_employee_card(row)
