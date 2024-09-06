from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Start
from aiogram_dialog.widgets.text import Case, Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import MagicFilter

from application.common.dto import Pagination
from application.user.gateway import GetUsersFilters
from application.user.interactors.get_users import GetUsers, GetUsersDTO
from entities.user.models import UserId
from presentation.admin.consts import STAFF_BTN_TXT
from presentation.admin.handlers.admin.staff.main import states
from presentation.admin.handlers.admin.staff.add_user_to_staff.states import (
    ChangeUserRole
)
from presentation.admin.handlers.admin.staff.view_staff_card.states import (
    ViewStaff
)

router = Router()


@router.message(Command("staff"))
@router.message(F.text == STAFF_BTN_TXT)
async def staff_workflow_btn(
        _: Message,
        dialog_manager: DialogManager
):
    await dialog_manager.start(
            state=states.StaffWorkflow.MAIN_MENU,
            mode=StartMode.RESET_STACK
    )


@inject
async def get_user_from_staff(
        action: FromDishka[GetUsers],
        dialog_manager: DialogManager,
        **_kwargs
) -> dict[str, Any]:
    result = await action(
            GetUsersDTO(
                    pagination=Pagination(),
                    filters=GetUsersFilters(

                    )
            )
    )

    dialog_manager.dialog_data["total"] = result.total
    dialog_manager.dialog_data["user"] = result.users

    return dialog_manager.dialog_data


is_only_admin_in_staff: MagicFilter = F["dialog_data"]["total"] == 1


async def on_selected_user_from_staff(
        _: CallbackQuery,
        __: Select,
        manager: DialogManager,
        user_id: UserId
):
    await manager.start(
            state=ViewStaff.STAFF_CARD,
            data={
                "user_id": user_id
            },
            mode=StartMode.RESET_STACK
    )


staff_workflow_dialog = Dialog(
        Window(
                Case(
                        {
                            False: Format(
                                    "<b>Всього співробітників:</b> "
                                    "{dialog_data[total]}"
                            ),
                            True: Const("У вас немає співробітників")
                        },
                        selector=is_only_admin_in_staff
                ),
                ScrollingGroup(
                        Start(
                                Const("➕ Додати співробітника"),
                                id="add_user_to_staff",
                                state=ChangeUserRole.ID,
                        ),
                        Select(
                                id="select_user_from_staff",
                                text=Format(
                                        "{item.full_name} | {item.role.value}"
                                ),
                                items="user",
                                item_id_getter=lambda item: item.user_id,
                                type_factory=lambda item: UserId(int(item)),
                                on_click=on_selected_user_from_staff
                        ),
                        id="staff_list",
                        hide_on_single_page=True,
                        width=1,
                        height=5,
                ),
                state=states.StaffWorkflow.MAIN_MENU,
                getter=get_user_from_staff
        )
)
