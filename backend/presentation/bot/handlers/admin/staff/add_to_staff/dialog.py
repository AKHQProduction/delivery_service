import operator
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Group,
    Row,
    Select,
    Start
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.change_user_role import ChangeUserRole, ChangeUserRoleDTO
from application.errors.user import UserIsNotExistError
from application.get_user import GetUser, GetUserInputDTO
from domain.entities.user import RoleName
from . import states
from ..states import StaffWorkflow


@inject
async def find_user(
        msg: Message,
        _: ManagedTextInput,
        manager: DialogManager,
        value: int,
        action: FromDishka[GetUser]
):
    try:
        user = await action(GetUserInputDTO(user_id=value))

        manager.dialog_data["user_id"] = user.user_id
        manager.dialog_data["full_name"] = user.full_name
        manager.dialog_data["username"] = user.username
        manager.dialog_data["phone_number"] = user.phone_number

    except UserIsNotExistError:
        return await msg.answer("😥 Не вдалось знайти користувач з вказаним ID")

    await manager.next()


async def get_actual_roles(**_kwargs) -> dict[str, Any]:
    roles = [
        ("manager", "👩‍💻 Менеджер", RoleName.MANAGER.value),
        ("driver", "🚛 Драйвер", RoleName.DRIVER.value)
    ]

    return {
        "roles": roles
    }


async def on_role_selected(
        _: CallbackQuery,
        __: Select,
        manager: DialogManager,
        item_id: RoleName,
) -> None:
    manager.dialog_data["role"] = item_id

    await manager.next()


@inject
async def on_role_confirmed(
        call: CallbackQuery,
        _: Cancel,
        manager: DialogManager,
        action: FromDishka[ChangeUserRole]
):
    user_id: int = manager.dialog_data["user_id"]
    role: str = manager.dialog_data["role"]

    await action(
            ChangeUserRoleDTO(
                    user_id=user_id,
                    role=RoleName(role)
            )
    )

    await call.message.answer("✅ Ви успішно додали співробітника")


add_to_staff_dialog = Dialog(
        Window(
                Const(
                        "Введіть телеграм ID користувача, "
                        "якого хочете додати до співробітників"
                ),
                TextInput(
                        id="new_staff_id",
                        type_factory=int,
                        on_success=find_user
                ),
                state=states.AddToStaff.ID
        ),
        Window(
                Multi(
                        Const("👀 Користувач знайден"),
                        Multi(
                                Format(
                                        "<b>Ім'я:</b> "
                                        "{dialog_data[full_name]}"
                                ),
                                Format(
                                        "<b>ID:</b> "
                                        "<code>{dialog_data[user_id]}</code>"
                                ),
                                Format(
                                        "<b>Username:</b> "
                                        "{dialog_data[username]}"
                                ),
                                Format(
                                        "<b>Номер телефону:</b> "
                                        "{dialog_data[phone_number]}"
                                )
                        ),
                        Const("Виберіть посаду👇"),
                        sep="\n\n"
                ),
                Group(
                        Select(
                                text=Format("{item[1]}"),
                                id="select_user_role",
                                items="roles",
                                item_id_getter=operator.itemgetter(2),
                                on_click=on_role_selected
                        ),
                        width=2
                ),
                state=states.AddToStaff.SELECT_USER_ROLE,
                getter=get_actual_roles
        ),
        Window(
                Const("Підтвердіть Ваше рішення"),
                Row(
                        Cancel(
                                text=Const("Так"),
                                id="accept_change_role",
                                on_click=on_role_confirmed
                        ),
                        Start(
                                text=Const("Ні"),
                                id="reject_change_role",
                                state=StaffWorkflow.MAIN_MENU
                        )
                ),
                state=states.AddToStaff.CONFIRMATION
        )
)
