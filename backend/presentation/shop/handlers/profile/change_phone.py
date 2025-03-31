import re

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format
from dishka.integrations.aiogram_dialog import inject

from presentation.common.consts import BACK_BTN_TXT

from . import states


def phone_number_formatter(value: str) -> str | None:
    pattern = re.compile(r"^\+380\d{9}$")

    if pattern.match(value):
        return value

    # 098...
    without_country_code_len = 10
    if len(value) == without_country_code_len:
        return f"+38{value}"

    # 380...
    with_count_code_len = 12
    if len(value) == with_count_code_len:
        return f"+{value}"

    return None


async def on_input_phone_number(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
):
    if phone_number := phone_number_formatter(value):
        manager.dialog_data["phone_number"] = phone_number
        await manager.next()
    else:
        await msg.answer("Ви ввели некоректний номер телефону")


@inject
async def on_accept_phone_number_change(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
):
    return manager.dialog_data["phone_number"]


change_phone_number_dialog = Dialog(
    Window(
        Const("Введіть Ваш номер телефону"),
        TextInput(
            id="new_phone_number_input", on_success=on_input_phone_number
        ),
        Cancel(Const(BACK_BTN_TXT)),
        state=states.ProfileChangePhone.NEW_PHONE,
    ),
    Window(
        Format(
            "Ви впевнені, що хочете змінити номер телефону "
            "на {dialog_data[phone_number]}"
        ),
        Row(
            Cancel(
                Const("Так"),
                id="accept_change_new_phone",
                on_click=on_accept_phone_number_change,  # noqa: ignore
            ),
            Cancel(Const("Ні"), id="reject_change_new_phone"),
        ),
        state=states.ProfileChangePhone.CONFIRMATION,
    ),
)
