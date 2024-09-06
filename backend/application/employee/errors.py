from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class EmployeeAlreadyExistsError(ApplicationError):
    @property
    def message(self):
        return f"Employee already exists"
