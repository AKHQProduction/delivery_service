from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start
from aiogram_dialog.widgets.text import Case, Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.dto import Pagination
from application.common.gateways.user import GetUsersFilters
from application.get_users import GetUsers, GetUsersDTO, GetUsersResultDTO
from domain.entities.user import RoleName, User
from presentation.bot.consts import STAFF_BTN_TXT
from . import states
from .add_to_staff.states import AddToStaff

router = Router()


@router.message(Command("/staff"))
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
async def get_staff(
        action: FromDishka[GetUsers],
        dialog_manager: DialogManager,
        **_kwargs
) -> dict[str, Any]:
    result = await action(
            GetUsersDTO(
                    pagination=Pagination(),
                    filters=GetUsersFilters(
                            roles=[
                                RoleName.ADMIN,
                                RoleName.MANAGER,
                                RoleName.DRIVER
                            ]
                    )
            )
    )

    dialog_manager.dialog_data["total"] = result.total
    dialog_manager.dialog_data["users"] = result.users

    return dialog_manager.dialog_data


def staff_main_menu_text_selector(
        _: dict,
        __: Case,
        manager: DialogManager
):
    return manager.dialog_data["total"] == 1


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
                        selector=staff_main_menu_text_selector
                ),
                Start(
                        Const("➕ Додати співробітника"),
                        id="add_to_staff",
                        state=AddToStaff.ID,
                        when=F["dialog_data"]["total"] == 1
                ),
                state=states.StaffWorkflow.MAIN_MENU,
                getter=get_staff
        )
)
# Window(
#
#         Const("👷‍♂️Робота з персоналом"),
#         Row(
#                 Start(
#                         Const("➕ Додати до персоналу"),
#                         id="add_to_staff",
#                         state=AddToStaff.ID
#                 ),
#                 Button(
#                         Const("➖ Прибрати з персоналу"),
#                         id="reject_from_staff"
#                 )
#         ),
#         Button(Const("👷 Персонал"), id="staff"),
#         state=states.StaffWorkflow.MAIN_MENU,
#         getter=get_staff
# )
