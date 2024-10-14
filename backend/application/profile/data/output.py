from dataclasses import dataclass

from entities.employee.models import EmployeeRole


@dataclass(frozen=True)
class UserProfileCardOutputData:
    user_id: int
    full_name: str
    username: str | None
    phone_number: str | None
    address: str | None
    employee_id: int | None = None
    role: EmployeeRole | None = None
