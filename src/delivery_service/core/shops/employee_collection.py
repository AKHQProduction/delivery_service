from delivery_service.core.shops.errors import (
    UserAlreadyInEmployeesError,
    UserNotFoundInEmployeesError,
)
from delivery_service.core.users.user import User, UserID


class EmployeeCollection(set[User]):
    def add_employee(self, employee: User) -> None:
        if employee in self:
            UserAlreadyInEmployeesError(employee.entity_id)

        self.add(employee)

    def get(self, employee_id: UserID) -> User:
        for employee in self:
            if employee.entity_id == employee_id:
                return employee
        raise UserNotFoundInEmployeesError(employee_id)

    def discard(self, employee: User) -> None:
        self.remove(employee)
