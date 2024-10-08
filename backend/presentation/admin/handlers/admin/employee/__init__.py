from aiogram import Dispatcher

from presentation.admin.handlers.admin.employee.main.dialog import (
    employee_workflow_dialog,
    router,
)

from .add_to_employee.dialog import add_to_employee_dialog
from .change_role.dialog import change_employee_role_dialog
from .remove_from_employee.dialog import remove_from_employee_dialog
from .view_employee.dialog import view_employee_card_dialog
from .view_employees.dialog import view_employee_cards_dialog


def setup_staff_workflow_handlers(dp: Dispatcher):
    dp.include_router(router)


def setup_staff_workflow_dialogs(dp: Dispatcher):
    dp.include_router(employee_workflow_dialog)
    dp.include_router(add_to_employee_dialog)
    dp.include_router(view_employee_card_dialog)
    dp.include_router(view_employee_cards_dialog)
    dp.include_router(remove_from_employee_dialog)
    dp.include_router(change_employee_role_dialog)


__all__ = ["setup_staff_workflow_dialogs", "setup_staff_workflow_handlers"]
