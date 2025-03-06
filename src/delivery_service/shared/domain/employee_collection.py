from delivery_service.shared.domain.employee import Employee
from delivery_service.shared.domain.identity_id import UserID
from delivery_service.shop_management.domain.errors import (
    UserAlreadyInEmployeesError,
    UserNotFoundInEmployeesError,
)


class EmployeeCollection(set[Employee]):
    def add_to_employees(self, employee: Employee) -> None:
        if employee in self:
            UserAlreadyInEmployeesError(employee.entity_id)

        self.add(employee)

    def get(self, employee_id: UserID) -> Employee:
        for employee in self:
            if employee.entity_id == employee_id:
                return employee
        raise UserNotFoundInEmployeesError(employee_id)

    def discard_from_employees(self, employee: Employee) -> None:
        self.discard(employee)
