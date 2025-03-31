from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Start
from aiogram_dialog.widgets.text import Case, Const, Format
from magic_filter import MagicFilter

from entities.employee.models import EmployeeId
from entities.user.models import UserId
from presentation.admin.handlers.admin.employee import states
from presentation.admin.handlers.admin.employee.common import (
    get_employee_cards,
)
from presentation.admin.handlers.admin.employee.states import AddToEmployee
from presentation.common.consts import EMPLOYEES_BTN_TXT

router = Router()


@router.message(Command("employee"))
@router.message(F.text == EMPLOYEES_BTN_TXT)
async def run_employee_workflow_dialog(
    _: Message, dialog_manager: DialogManager
):
    await dialog_manager.start(
        state=states.EmployeeWorkflow.MAIN_MENU,
        mode=StartMode.RESET_STACK,
    )


is_only_admin_in_employees: MagicFilter = F["dialog_data"]["total"] == 1


async def on_selected_employee_from_list(
    _: CallbackQuery,
    __: Select,
    manager: DialogManager,
    value: UserId,
):
    await manager.start(
        state=states.ViewEmployee.VIEW, data={"employee_id": value}
    )


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
        ScrollingGroup(
            Select(
                id="select_employee_from_cards",
                text=Format("{item[2]} | {item[3]}"),
                items="employee_cards",
                item_id_getter=lambda item: item[0],
                type_factory=lambda item: EmployeeId(item),
                on_click=on_selected_employee_from_list,
            ),
            id="employee_cards_list",
            hide_on_single_page=True,
            width=2,
            height=10,
            when=~is_only_admin_in_employees,
        ),
        state=states.EmployeeWorkflow.MAIN_MENU,
        getter=get_employee_cards,
    ),
)
