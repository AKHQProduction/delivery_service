from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Cancel, Row, Start
from aiogram_dialog.widgets.text import Const
from dishka.integrations.aiogram_dialog import inject

from presentation.admin.handlers.admin.staff.main.states import StaffWorkflow

from .states import DeleteUserFromStaff


async def on_start_delete_user_from_staff_dialog(
    data: dict[str, Any],
    manager: DialogManager,
):
    manager.dialog_data["user_id"] = data["user_id"]


@inject
async def handle_change_role_to_user(
    call: CallbackQuery,
    _: Cancel,
    __: DialogManager,
):
    await call.answer("✅ Ви успішно видалили співробітника")


delete_user_from_staff_dialog = Dialog(
    Window(
        Const("Підтвердіть Ваше рішення"),
        Row(
            Start(
                text=Const("Так"),
                id="accept_change_role_to_user",
                on_click=handle_change_role_to_user,
                state=StaffWorkflow.MAIN_MENU,
                mode=StartMode.RESET_STACK,
            ),
            Start(
                text=Const("Ні"),
                id="reject_change_role",
                state=StaffWorkflow.MAIN_MENU,
                mode=StartMode.RESET_STACK,
            ),
        ),
        state=DeleteUserFromStaff.CONFIRMATION,
    ),
    on_start=on_start_delete_user_from_staff_dialog,
)
