import operator

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Group,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.commands.employee.edit_employee import (
    ChangeEmployeeCommand,
    ChangeEmployeeCommandHandler,
)
from application.common.persistence.employee import EmployeeReader
from entities.employee.models import EmployeeRole
from presentation.common.consts import ACTUAL_ROLES, BACK_BTN_TXT

from . import states
from .common import employee_card, get_actual_employee_roles


async def on_successfully_input(
    key: str, value: str, manager: DialogManager
) -> None:
    manager.dialog_data[key] = value
    manager.dialog_data["is_edited"] = True

    await manager.switch_to(state=states.EditEmployee.MAIN)


@inject
async def on_save_editing_employee(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    action: FromDishka[ChangeEmployeeCommandHandler],
):
    await action(
        ChangeEmployeeCommand(
            employee_id=manager.dialog_data["employee_id"],
            role=manager.dialog_data["role"],
        )
    )


edit_employee_kb = Group(
    SwitchTo(
        state=states.EditEmployee.ROLE,
        id="edit_employee_role",
        text=Const("👷‍♂️ Змінити роль"),
    ),
    Cancel(
        id="save_after_edit_employee",
        text=Const("💾 Зберегти"),
        when=F["dialog_data"]["is_edited"],
        on_click=on_save_editing_employee,  # noqa: ignore
    ),
    Cancel(Const(BACK_BTN_TXT)),
)


@inject
async def on_start_edit_employee_dialog(
    data: Data,
    manager: DialogManager,
    employee_reader: FromDishka[EmployeeReader],
) -> None:
    employee_id = data.get("employee_id")

    employee = await employee_reader.read_with_id(employee_id)
    if not employee:
        return

    manager.dialog_data["employee_id"] = employee_id
    manager.dialog_data["full_name"] = employee.full_name
    manager.dialog_data["role"] = employee.role
    manager.dialog_data["role_txt"] = ACTUAL_ROLES[employee.role]


async def on_new_role_selected(
    _: CallbackQuery, __: Select, manager: DialogManager, value: EmployeeRole
) -> None:
    manager.dialog_data["role"] = value
    manager.dialog_data["role_txt"] = ACTUAL_ROLES[value]
    manager.dialog_data["is_edited"] = True

    await manager.switch_to(state=states.EditEmployee.MAIN)


edit_employee_dialog = Dialog(
    Window(employee_card, edit_employee_kb, state=states.EditEmployee.MAIN),
    Window(
        Multi(
            employee_card, Const("<b>Оберіть нову посаду 👇</b>"), sep="\n\n"
        ),
        Group(
            Select(
                text=Format("{item[1]}"),
                id="select_employee_role",
                items="roles",
                item_id_getter=operator.itemgetter(0),
                type_factory=lambda x: EmployeeRole(x),
                on_click=on_new_role_selected,
            ),
            width=2,
        ),
        Back(Const(BACK_BTN_TXT), id="back_to_start_edit_employee_menu"),
        state=states.EditEmployee.ROLE,
        getter=get_actual_employee_roles,
    ),
    on_start=on_start_edit_employee_dialog,  # noqa: ignore
)
