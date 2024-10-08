import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Row,
    ScrollingGroup,
    Select,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format

from presentation.common.consts import BACK_BTN_TXT

from ..getters import get_employee_cards
from ..main.states import EmployeeWorkflow
from ..view_employee.states import ViewEmployee
from . import states


async def on_selected_employee_from_list(
    _: CallbackQuery,
    __: Select,
    manager: DialogManager,
    value: int,
):
    await manager.start(state=ViewEmployee.VIEW, data={"employee_id": value})


view_employee_cards_dialog = Dialog(
    Window(
        Const("📋 Список співробітників"),
        ScrollingGroup(
            Select(
                id="select_employee_from_cards",
                text=Format("{item[2]} | {item[3]}"),
                items="employee_cards",
                item_id_getter=operator.itemgetter(0),
                type_factory=int,
                on_click=on_selected_employee_from_list,
            ),
            id="employee_cards_list",
            hide_on_single_page=True,
            width=2,
            height=10,
        ),
        Row(
            Start(
                Const(BACK_BTN_TXT),
                id="back_to_employee_menu_from_list",
                state=EmployeeWorkflow.MAIN_MENU,
            )
        ),
        state=states.ViewEmployees.VIEW,
        getter=get_employee_cards,
    ),
)
