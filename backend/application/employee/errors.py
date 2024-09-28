from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class EmployeeAlreadyExistError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"Employee already exist with user_id={self.user_id}"


@dataclass(eq=False)
class EmployeeNotFoundError(ApplicationError):
    employee_id: int

    @property
    def message(self):
        return f"Employee with id={self.employee_id} not exist"
