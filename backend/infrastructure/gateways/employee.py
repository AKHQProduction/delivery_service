from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.employee.errors import EmployeeAlreadyExistsError
from application.employee.gateway import EmployeeReader, EmployeeSaver
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
        except IntegrityError:
            raise EmployeeAlreadyExistsError()

    async def by_identity(self, user_id: UserId) -> Employee | None:
        query = select(Employee).where(employees_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete(self, employee_id: EmployeeId) -> None:
        query = delete(
                Employee
        ).where(
                employees_table.c.employee_id == employee_id
        )

        await self.session.execute(query)
