import logging

from entities.common.tracker import Tracker
from entities.employee.errors import AdminRoleChangeRestrictedError
from entities.employee.models import Employee, EmployeeRole
from entities.shop.models import ShopId
from entities.user.models import UserId


class EmployeeService:
    def __init__(self, tracker: Tracker) -> None:
        self.tracker = tracker

    def add_employee(
        self,
        shop_id: ShopId,
        user_id: UserId,
        role: EmployeeRole = EmployeeRole.ADMIN,
    ) -> Employee:
        new_employee = Employee(
            oid=None, user_id=user_id, shop_id=shop_id, role=role
        )

        self.tracker.add_one(new_employee)

        return new_employee


def change_employee_role(employee: Employee, new_role: EmployeeRole) -> None:
    if employee.role == EmployeeRole.ADMIN:
        raise AdminRoleChangeRestrictedError(employee.user_id)

    if employee.role == new_role:
        return

    old_role = employee.role
    employee.role = new_role

    logging.info(
        "Employee with id %s successfully changed role from %s to %s",
        employee.oid,
        old_role,
        new_role,
    )
