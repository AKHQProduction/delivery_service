from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Cancel,
    Row,
)
from aiogram_dialog.widgets.text import Const, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.employee.commands.add_employee import (
    AddEmployee,
    AddEmployeeInputData,
)
from application.employee.errors import EmployeeAlreadyExistError
from application.user.errors import UserNotFoundError
from application.user.interactors.get_user import GetUser, GetUserInputData
from presentation.common.consts import (
    BACK_BTN_TXT,
    CANCEL_BTN_TXT,
)
from presentation.common.widgets.common.cancel_btn import (
    dialog_has_mistakes_in_input,
    setup_input_error_flag,
)

from ..common.widgets import (
    get_actual_employee_roles,
    select_employee_role_widget,
)
from . import states


@inject
async def on_success_input_user_id(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: int,
    action: FromDishka[GetUser],
):
    try:
        await action(GetUserInputData(value))

        manager.dialog_data["user_id"] = value
        await manager.next()

    except UserNotFoundError:
        await msg.answer("Користувач з таким ID не знайден")
        setup_input_error_flag(manager, flag=True)


@inject
async def on_role_confirmed(
    call: CallbackQuery,
    _: Cancel,
    manager: DialogManager,
    action: FromDishka[AddEmployee],
):
    try:
        await action(
            AddEmployeeInputData(
                user_id=manager.dialog_data["user_id"],
                role=manager.dialog_data["role"],
            )
        )

        await call.answer("✅ Ви успішно додали співробітника")

    except EmployeeAlreadyExistError:
        await call.message.answer("❌ Користувач вже в складі персоналу")


add_to_employee_dialog = Dialog(
    Window(
        Const(
            "Введіть телеграм ID користувача, якого хочете додати до "
            "співробітників",
        ),
        TextInput(
            id="new_staff_id",
            type_factory=int,
            on_success=on_success_input_user_id,  # noqa: ignore
        ),
        Cancel(
            id="back_to_employee_main_menu",
            text=Const(BACK_BTN_TXT),
            when=dialog_has_mistakes_in_input,
        ),
        state=states.AddToEmployee.FIND,
    ),
    Window(
        Multi(
            Const("Користувач знайден"), Const("Виберіть посаду👇"), sep="\n\n"
        ),
        select_employee_role_widget,
        Row(Cancel(Const(CANCEL_BTN_TXT))),
        Row(Back(Const(BACK_BTN_TXT))),
        state=states.AddToEmployee.SELECT_EMPLOYEE_ROLE,
        getter=get_actual_employee_roles,
    ),
    Window(
        Const("Підтвердіть Ваше рішення"),
        Row(
            Cancel(
                text=Const("Так"),
                id="accept_add_to_employee",
                on_click=on_role_confirmed,  # type: ignore[arg-type]
            ),
            Cancel(
                text=Const("Ні"),
                id="reject_add_to_employee",
            ),
        ),
        state=states.AddToEmployee.CONFIRMATION,
    ),
)
