from dataclasses import dataclass

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class EmployeeAlreadyExistsError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"Employee already exists with user_id={self.user_id}"


@dataclass(eq=False)
class EmployeeNotFoundError(ApplicationError):
    employee_id: int | None = None

    @property
    def message(self):
        return f"Employee with id={self.employee_id} not exists"
