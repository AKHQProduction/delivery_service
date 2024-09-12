from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from presentation.admin.dialogs.getters.user import get_user_getter
from presentation.admin.dialogs.widgets.user.user_card import user_card

from ..delete_user_from_staff.states import DeleteUserFromStaff
from .states import ViewStaff


async def on_start_view_staff_card_dialog(
    data: dict[str, Any], manager: DialogManager
):
    manager.dialog_data["user_id"] = data["user_id"]


async def handle_delete_from_user_btn(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
):
    await manager.start(
        state=DeleteUserFromStaff.CONFIRMATION,
        data={"user_id": manager.dialog_data["user_id"]},
    )


view_staff_card_dialog = Dialog(
    Window(
        user_card,
        Button(
            id="delete_from_staff",
            text=(Const("Прибрати з персоналу")),
            on_click=handle_delete_from_user_btn,
        ),
        state=ViewStaff.STAFF_CARD,
        getter=get_user_getter,
    ),
    on_start=on_start_view_staff_card_dialog,
)
