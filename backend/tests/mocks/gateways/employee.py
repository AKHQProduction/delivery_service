from application.employee.errors import (
    EmployeeAlreadyExistError,
    EmployeeNotFoundError,
)
from application.employee.gateway import (
    EmployeeGateway,
)
from entities.employee.models import Employee, EmployeeId, EmployeeRole
from entities.shop.models import ShopId
from entities.user.models import UserId


class FakeEmployeeGateway(EmployeeGateway):
    def __init__(self):
        self.employees: dict[int, Employee] = {
            1: Employee(
                employee_id=EmployeeId(1),
                user_id=UserId(1),
                shop_id=ShopId(1234567898),
                role=EmployeeRole.ADMIN,
            ),
            2: Employee(
                employee_id=EmployeeId(2),
                user_id=UserId(3),
                shop_id=ShopId(1234567898),
                role=EmployeeRole.MANAGER,
            ),
        }

        self.saved = False
        self.deleted = False

        self._next_id = 2

    async def save(self, employee: Employee) -> None:
        employee = await self.by_identity(employee.user_id)

        if employee:
            raise EmployeeAlreadyExistError(employee.user_id)

        self.employees[self._next_id] = employee

        self.saved = True
        self._next_id += 1

    async def by_identity(self, user_id: UserId) -> Employee | None:
        return next(
            (
                employee
                for employee in list(self.employees.values())
                if employee.user_id == user_id
            ),
            None,
        )

    async def delete(self, employee_id: EmployeeId) -> None:
        employee = self.employees.get(employee_id, None)

        if not employee:
            raise EmployeeNotFoundError(employee_id)

        del self.employees[employee_id]

        self.deleted = True
