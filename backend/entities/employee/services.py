import logging

from entities.employee.errors import AdminRoleChangeRestrictedError
from entities.employee.models import Employee, EmployeeRole


def change_employee_role(employee: Employee, new_role: EmployeeRole) -> None:
    if employee.role == EmployeeRole.ADMIN:
        raise AdminRoleChangeRestrictedError(employee.user_id)

    if employee.role == new_role:
        return

    old_role = employee.role
    employee.role = new_role

    logging.info(
        "Employee with id %s successfully changed role from %s to %s",
        employee.employee_id,
        old_role,
        new_role,
    )
