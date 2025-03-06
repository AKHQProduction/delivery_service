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

from application.commands.employee.add_employee import (
    AddEmployeeCommand,
    AddEmployeeCommandHandler,
)
from application.common.errors.employee import EmployeeAlreadyExistsError
from application.common.persistence.user import UserReader
from presentation.admin.handlers.admin.employee.common import (
    employee_card,
    get_actual_employee_roles,
    get_employee_card,
    select_employee_role_widget,
)
from presentation.common.consts import (
    BACK_BTN_TXT,
    CANCEL_BTN_TXT,
)
from presentation.common.widgets.common.cancel_btn import (
    setup_input_error_flag,
)

from . import states


@inject
async def on_success_input_user_id(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: int,
    user_reader: FromDishka[UserReader],
):
    user = await user_reader.read_profile_with_tg_id(value)

    if not user:
        await msg.answer("Користувач з таким ID не знайден")
        setup_input_error_flag(manager, flag=True)
    else:
        manager.dialog_data["user_id"] = value
        await manager.next()


@inject
async def on_role_confirmed(
    call: CallbackQuery,
    _: Cancel,
    manager: DialogManager,
    action: FromDishka[AddEmployeeCommandHandler],
):
    try:
        await action(
            AddEmployeeCommand(
                user_id=manager.dialog_data["user_id"],
                role=manager.dialog_data["role"],
            )
        )

        await call.answer("✅ Ви успішно додали співробітника")

    except EmployeeAlreadyExistsError:
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
        ),
        state=states.AddToEmployee.FIND,
    ),
    Window(
        Multi(
            Const("<b>Користувач знайден</b>"),
            employee_card,
            Const("Виберіть посаду👇"),
            sep="\n\n",
        ),
        select_employee_role_widget,
        Row(Cancel(Const(CANCEL_BTN_TXT))),
        Row(Back(Const(BACK_BTN_TXT))),
        state=states.AddToEmployee.SELECT_EMPLOYEE_ROLE,
        getter=[get_actual_employee_roles, get_employee_card],
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
