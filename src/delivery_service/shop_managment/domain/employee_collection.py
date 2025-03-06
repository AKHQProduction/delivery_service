from delivery_service.identity.domain.user import User, UserID
from delivery_service.shop_managment.domain.errors import (
    UserAlreadyInEmployeesError,
    UserNotFoundInEmployeesError,
)


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
