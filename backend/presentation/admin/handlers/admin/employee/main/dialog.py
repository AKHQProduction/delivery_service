from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Case, Const, Format
from magic_filter import MagicFilter

from presentation.admin.handlers.admin.employee.add_to_employee import (
    AddToEmployee,
)
from presentation.admin.handlers.admin.employee.getters import (
    get_employee_cards,
)
from presentation.admin.handlers.admin.employee.main import states
from presentation.admin.handlers.admin.employee.view_employees.states import (
    ViewEmployees,
)
from presentation.common.consts import EMPLOYEE_BTN_TXT

router = Router()


@router.message(Command("employee"))
@router.message(F.text == EMPLOYEE_BTN_TXT)
async def run_employee_workflow_dialog(
    _: Message, dialog_manager: DialogManager
):
    await dialog_manager.start(
        state=states.EmployeeWorkflow.MAIN_MENU,
        mode=StartMode.RESET_STACK,
    )


is_only_admin_in_employees: MagicFilter = F["dialog_data"]["total"] == 1

employee_workflow_dialog = Dialog(
    Window(
        Case(
            {
                False: Format(
                    "<b>Всього співробітників:</b> {dialog_data[total]}"
                ),
                True: Const("У вас немає співробітників"),
            },
            selector=is_only_admin_in_employees,
        ),
        Start(
            Const("➕ Додати співробітника"),
            id="add_to_employee",
            state=AddToEmployee.FIND,
        ),
        Start(
            Const("📋 Список співробітників"),
            id="show_employee_cards",
            state=ViewEmployees.VIEW,
            mode=StartMode.RESET_STACK,
            when=~is_only_admin_in_employees,
        ),
        state=states.EmployeeWorkflow.MAIN_MENU,
        getter=get_employee_cards,
    ),
)
