from dataclasses import asdict
from typing import Any

from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.persistence.user import UserReader
from presentation.common.consts import PROFILE_BTN_TXT

from . import states

router = Router()


@router.message(F.text == PROFILE_BTN_TXT)
async def shop_profile_btn_handler(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.ProfileMenu.MAIN, mode=StartMode.RESET_STACK
    )


profile_card = Multi(
    Const("👀 Картка користувача"),
    Multi(
        Format("<b>🆔 Телеграм ID:</b> <code>{dialog_data[tg_id]}</code>"),
        Format("<b>💁🏼‍♂️ Ім'я: </b>{dialog_data[full_name]}"),
        Case(
            {
                ...: Format(
                    "<b>🪪 Телеграм тег:</b> @{dialog_data[username]}"
                ),
                None: Const("<b>🪪 Телеграм тег:</b> <i>відсутній</i>"),
            },
            selector=F["dialog_data"]["username"],
        ),
        Case(
            {
                ...: Format(
                    "<b>📞 Номер телефону:</b> {dialog_data[phone_number]}"
                ),
                None: Const("<b>📞 Номер телефону:</b> <i>відсутній</i>"),
            },
            selector=F["dialog_data"]["phone_number"],
        ),
        Case(
            {
                ...: Format("<b>📍 Адреса:</b> {dialog_data[address]}"),
                None: Const("<b>📍 Адреса:</b> <i>відсутня</i>"),
            },
            selector=F["dialog_data"]["address"],
        ),
    ),
    sep="\n\n",
)


@inject
async def get_profile_card(
    dialog_manager: DialogManager,
    user_reader: FromDishka[UserReader],
    **_kwargs,
) -> dict[str, Any]:
    tg_id = dialog_manager.dialog_data.get(
        "tg_id", dialog_manager.event.from_user.id
    )

    user_profile = await user_reader.read_profile_with_tg_id(tg_id=int(tg_id))

    profile_data = asdict(user_profile)
    profile_data["address"] = user_profile.address.full_address

    dialog_manager.dialog_data.update(profile_data)

    return dialog_manager.dialog_data


profile_main_dialog = Dialog(
    Window(
        profile_card,
        Row(
            Start(
                Const("Змінити телефон"),
                state=states.ProfileChangePhone.NEW_PHONE,
                id="start_change_phone_dialog",
            ),
            Start(
                Const("Змінити адресу"),
                state=states.ProfileChangeAddress.NEW_ADDRESS,
                id="start_change_address_dialog",
            ),
        ),
        state=states.ProfileMenu.MAIN,
    ),
    getter=get_profile_card,
)
