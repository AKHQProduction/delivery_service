from aiogram import Dispatcher

from presentation.admin.handlers.admin.employee.add import (
    add_to_employee_dialog,
)
from presentation.admin.handlers.admin.employee.main import (
    employee_workflow_dialog,
    router,
)
from presentation.admin.handlers.admin.employee.view import (
    view_employee_card_dialog,
)

from .edit import edit_employee_dialog


def setup_employee_workflow_handlers(dp: Dispatcher):
    dp.include_router(router)


def setup_employee_workflow_dialogs(dp: Dispatcher):
    dp.include_router(employee_workflow_dialog)
    dp.include_router(add_to_employee_dialog)
    dp.include_router(view_employee_card_dialog)
    dp.include_router(edit_employee_dialog)


__all__ = [
    "setup_employee_workflow_dialogs",
    "setup_employee_workflow_handlers",
]
