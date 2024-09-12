import operator
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Cancel, Group, Row, Select, Start
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka.integrations.aiogram_dialog import inject

from presentation.admin.dialogs.getters.user import get_user_getter
from presentation.admin.dialogs.widgets.user.user_card import user_card
from presentation.admin.handlers.admin.staff.main.states import StaffWorkflow

from . import states


async def on_success_input_user_id(
    _: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: int,
):
    manager.dialog_data["user_id"] = value

    await manager.next()


async def get_actual_staff_roles(**_kwargs) -> dict[str, Any]:
    return {"roles": None}


async def on_role_selected(
    _: CallbackQuery,
    __: Select,
    manager: DialogManager,
) -> None:
    manager.dialog_data["role"] = None

    await manager.next()


@inject
async def on_role_confirmed(
    call: CallbackQuery,
    _: Cancel,
    __: DialogManager,
):
    await call.answer("✅ Ви успішно додали співробітника")


add_user_to_staff_dialog = Dialog(
    Window(
        Const(
            "Введіть телеграм ID користувача, якого хочете додати до "
            "співробітників",
        ),
        TextInput(
            id="new_staff_id",
            type_factory=int,
            on_success=on_success_input_user_id,
        ),
        state=states.ChangeUserRole.ID,
    ),
    Window(
        Multi(user_card, Const("Виберіть посаду👇"), sep="\n\n"),
        Group(
            Select(
                text=Format("{item[1]}"),
                id="select_user_role",
                items="roles",
                item_id_getter=operator.itemgetter(2),
                type_factory=int,
                on_click=on_role_selected,
            ),
            width=2,
        ),
        state=states.ChangeUserRole.SELECT_USER_ROLE,
        getter=[get_actual_staff_roles, get_user_getter],
    ),
    Window(
        Const("Підтвердіть Ваше рішення"),
        Row(
            Cancel(
                text=Const("Так"),
                id="accept_change_role",
                on_click=on_role_confirmed,
            ),
            Start(
                text=Const("Ні"),
                id="reject_change_role",
                state=StaffWorkflow.MAIN_MENU,
                mode=StartMode.RESET_STACK,
            ),
        ),
        state=states.ChangeUserRole.CONFIRMATION,
    ),
)
