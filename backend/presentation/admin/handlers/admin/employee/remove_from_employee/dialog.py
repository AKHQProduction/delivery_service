from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Start
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.employee.commands.remove_employee import (
    RemoveEmployee,
    RemoveEmployeeInputData,
)

from ..view_employee.states import ViewEmployee
from ..view_employees.states import ViewEmployees
from .states import RemoveFromEmployee


async def on_start_remove_from_employee_dialog(
    data: dict[str, Any],
    manager: DialogManager,
):
    manager.dialog_data["employee_id"] = data["employee_id"]


@inject
async def handle_accept_remove_from_employee(
    call: CallbackQuery,
    _: Cancel,
    manager: DialogManager,
    action: FromDishka[RemoveEmployee],
):
    await action(RemoveEmployeeInputData(manager.dialog_data["employee_id"]))

    await call.answer("✅ Ви успішно видалили співробітника")


async def handle_reject_remove_from_employee(
    __: CallbackQuery,
    _: Button,
    manager: DialogManager,
):
    await manager.start(
        state=ViewEmployee.VIEW,
        mode=StartMode.RESET_STACK,
        data={"employee_id": manager.dialog_data["employee_id"]},
    )


remove_from_employee_dialog = Dialog(
    Window(
        Const("Підтвердіть Ваше рішення"),
        Row(
            Start(
                text=Const("Так"),
                id="accept_change_role_to_user",
                on_click=handle_accept_remove_from_employee,  # noqa: ignore
                state=ViewEmployees.VIEW,
                mode=StartMode.RESET_STACK,
            ),
            Button(
                text=Const("Ні"),
                on_click=handle_reject_remove_from_employee,
                id="reject_change_role",
            ),
        ),
        state=RemoveFromEmployee.CONFIRMATION,
    ),
    on_start=on_start_remove_from_employee_dialog,
)
