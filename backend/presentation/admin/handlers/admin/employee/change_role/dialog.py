from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.employee.commands.change_employee_role import (
    ChangeEmployeeRole,
    ChangeEmployeeRoleInputData,
)
from application.employee.query.get_employee_card import (
    GetEmployeeCard,
    GetEmployeeCardInputData,
)
from presentation.common.consts import ACTUAL_ROLES, CANCEL_BTN_TXT

from ..common.widgets import (
    get_actual_employee_roles,
    select_employee_role_widget,
)
from . import states


async def on_start_change_employee_role_dialog(
    data: dict[str, Any],
    manager: DialogManager,
):
    manager.dialog_data["employee_id"] = data["employee_id"]


@inject
async def on_close_change_employee_role_dialog(
    _: dict[str, Any],
    manager: DialogManager,
    action: FromDishka[GetEmployeeCard],
):
    employee_id = manager.dialog_data["employee_id"]

    output_data = await action(GetEmployeeCardInputData(employee_id))

    manager.dialog_data["user_id"] = output_data.user_id
    manager.dialog_data["employee_id"] = employee_id
    manager.dialog_data["role"] = ACTUAL_ROLES[output_data.role]


@inject
async def on_accept_role_change(
    _: CallbackQuery,
    __: Cancel,
    manager: DialogManager,
    action: FromDishka[ChangeEmployeeRole],
):
    await action(
        ChangeEmployeeRoleInputData(
            employee_id=manager.dialog_data["employee_id"],
            role=manager.dialog_data["role"],
        )
    )

    await manager.done({"role": manager.dialog_data["role"]})


change_employee_role_dialog = Dialog(
    Window(
        Const("Виберіть посаду👇"),
        select_employee_role_widget,
        Row(Cancel(Const(CANCEL_BTN_TXT))),
        state=states.ChangeRole.SELECT_EMPLOYEE_ROLE,
        getter=get_actual_employee_roles,
    ),
    Window(
        Const("Підтвердіть Ваше рішення"),
        Row(
            Button(
                text=Const("Так"),
                id="accept_change_employee_role",
                on_click=on_accept_role_change,  # type: ignore[arg-type]
            ),
            Cancel(
                text=Const("Ні"),
                id="reject_change_employee_role",
            ),
        ),
        state=states.ChangeRole.CONFIRMATION,
    ),
    on_start=on_start_change_employee_role_dialog,
    on_close=on_close_change_employee_role_dialog,  # noqa: ignore
)
