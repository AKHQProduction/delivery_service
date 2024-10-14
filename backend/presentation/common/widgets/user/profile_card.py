from dataclasses import asdict
from typing import Any

from aiogram import F
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.profile.queries.get_profile_card import (
    GetProfileCard,
    GetProfileCardInputData,
)
from presentation.common.consts import ACTUAL_ROLES


@inject
async def get_profile_card(
    dialog_manager: DialogManager,
    action: FromDishka[GetProfileCard],
    **_kwargs,
) -> dict[str, Any]:
    user_id = dialog_manager.dialog_data.get(
        "user_id", dialog_manager.event.from_user.id
    )

    user_profile_card = await action(
        GetProfileCardInputData(user_id=int(user_id))
    )

    dialog_manager.dialog_data.update(asdict(user_profile_card))
    if role := user_profile_card.role:
        dialog_manager.dialog_data["role_txt"] = ACTUAL_ROLES[role]

    return dialog_manager.dialog_data


profile_card = Multi(
    Const("👀 Картка користувача \n"),
    Format(text="{role_txt} \n", when=F["role"]),
    Format("<b>🆔 Телеграм ID:</b> <code>{user_id}</code>"),
    Format("<b>💁🏼‍♂️ Ім'я: </b>{full_name}"),
    Case(
        {
            ...: Format("<b>🪪 Телеграм тег:</b> @{username}"),
            None: Const("<b>🪪 Телеграм тег:</b> <i>відсутній</i>"),
        },
        selector=F["username"],
    ),
    Case(
        {
            ...: Format("<b>📞 Номер телефону:</b> {phone_number}"),
            None: Const("<b>📞 Номер телефону:</b> <i>відсутній</i>"),
        },
        selector=F["phone_number"],
    ),
    Case(
        {
            ...: Format("<b>📍 Адреса:</b> {address}"),
            None: Const("<b>📍 Адреса:</b> <i>відсутня</i>"),
        },
        selector=F["address"],
    ),
)
