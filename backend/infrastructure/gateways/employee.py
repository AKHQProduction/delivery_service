from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.employee.errors import EmployeeAlreadyExistsError
from application.employee.gateway import EmployeeSaver
from entities.employee.models import Employee


class EmployeeGateway(EmployeeSaver):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def save(self, employee: Employee) -> None:
        self.session.add(employee)

        try:
            await self.session.flush()
        except IntegrityError:
            raise EmployeeAlreadyExistsError()
