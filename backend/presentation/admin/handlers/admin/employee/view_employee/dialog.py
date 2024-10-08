from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.employee.query.get_employee_card import (
    GetEmployeeCard,
    GetEmployeeCardInputData,
)
from presentation.common.consts import ACTUAL_ROLES, BACK_BTN_TXT
from presentation.common.widgets.user.profile_card import (
    get_profile_card,
    profile_card,
)

from ..change_role.states import ChangeRole
from ..remove_from_employee.states import RemoveFromEmployee
from .states import ViewEmployee


@inject
async def on_start_view_employee_card_dialog(
    data: dict[str, Any],
    manager: DialogManager,
    action: FromDishka[GetEmployeeCard],
):
    employee_id = data.get("employee_id")

    output_data = await action(GetEmployeeCardInputData(employee_id))

    manager.dialog_data["user_id"] = output_data.user_id
    manager.dialog_data["employee_id"] = employee_id
    manager.dialog_data["role"] = ACTUAL_ROLES[output_data.role]


async def handle_delete_from_employee_btn(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
):
    await manager.start(
        state=RemoveFromEmployee.CONFIRMATION,
        data={"employee_id": manager.dialog_data["employee_id"]},
    )


async def handle_change_employee_role_btn(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
):
    await manager.start(
        state=ChangeRole.SELECT_EMPLOYEE_ROLE,
        data={"employee_id": manager.dialog_data["employee_id"]},
    )


async def handle_result_from_change_employee_role(
    _: Data,
    result: Any,
    manager: DialogManager,
):
    if result:
        manager.dialog_data["role"] = ACTUAL_ROLES[result["role"]]


view_employee_card_dialog = Dialog(
    Window(
        profile_card,
        Button(
            id="remove_from_employee",
            text=Const("Видалити з персоналу"),
            on_click=handle_delete_from_employee_btn,
        ),
        Button(
            text=Const("Змінить посаду"),
            id="change_employee_role",
            on_click=handle_change_employee_role_btn,
        ),
        Cancel(
            Const(BACK_BTN_TXT),
            id="back_from_employee_detail",
        ),
        state=ViewEmployee.VIEW,
        getter=get_profile_card,
    ),
    on_start=on_start_view_employee_card_dialog,  # noqa: ignore
    on_process_result=handle_result_from_change_employee_role,
)
