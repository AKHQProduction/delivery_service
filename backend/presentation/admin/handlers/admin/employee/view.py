from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row
from aiogram_dialog.widgets.text import Const, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.commands.employee.remove_employee import (
    RemoveEmployeeCommand,
    RemoveEmployeeCommandHandler,
)
from presentation.common.consts import BACK_BTN_TXT
from presentation.common.helpers import default_on_start_handler

from . import states
from .common import employee_card, get_employee_card


@inject
async def handle_accept_remove_from_employee(
    call: CallbackQuery,
    _: Cancel,
    manager: DialogManager,
    action: FromDishka[RemoveEmployeeCommandHandler],
):
    await action(RemoveEmployeeCommand(manager.dialog_data["employee_id"]))

    await call.answer("✅ Ви успішно видалили співробітника")


async def on_change_employee_btn(
    _: CallbackQuery, __: Button, manager: DialogManager
) -> None:
    await manager.start(
        state=states.EditEmployee.MAIN,
        data={"employee_id": manager.dialog_data["employee_id"]},
    )


view_employee_card_dialog = Dialog(
    Window(
        employee_card,
        Button(
            text=Const("✏️ Редагувати"),
            id="change_employee_role",
            on_click=on_change_employee_btn,
        ),
        Next(
            id="remove_from_employee",
            text=Const("🗑 Видалити"),
        ),
        Cancel(
            Const(BACK_BTN_TXT),
            id="back_from_employee_detail",
        ),
        state=states.ViewEmployee.VIEW,
    ),
    Window(
        Multi(
            employee_card, Const("<b>Підтвердіть видалення</b>"), sep="\n\n"
        ),
        Row(
            Cancel(
                Const("Так"),
                id="back_to_employees_list",
                on_click=handle_accept_remove_from_employee,  # noqa: ignore
            ),
            Back(Const("Ні"), id="back_to_employee_card"),
        ),
        state=states.ViewEmployee.DELETE,
    ),
    on_start=default_on_start_handler,
    getter=get_employee_card,
)
