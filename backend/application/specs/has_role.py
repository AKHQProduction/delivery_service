from application.common.specification import Specification
from entities.employee.models import EmployeeRole


class HasRoleSpec(Specification):
    def __init__(self, role: EmployeeRole):
        self._role = role

    def is_satisfied_by(self, candidate: EmployeeRole) -> bool:
        return self._role == candidate
