from dataclasses import dataclass

from entities.employee.models import EmployeeRole


@dataclass(frozen=True)
class EmployeeCard:
    employee_id: int
    user_id: int
    full_name: str
    role: EmployeeRole
