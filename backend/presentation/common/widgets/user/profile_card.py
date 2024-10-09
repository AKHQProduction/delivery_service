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


@inject
async def get_profile_card(
    dialog_manager: DialogManager,
    action: FromDishka[GetProfileCard],
    **_kwargs,
) -> dict[str, Any]:
    user_id = dialog_manager.dialog_data["user_id"]

    user_profile_card = await action(GetProfileCardInputData(user_id=user_id))

    return {"profile_card": asdict(user_profile_card)}


profile_card = Multi(
    Const("👀 Картка користувача \n"),
    Format(text="{dialog_data[role]} \n", when=F["dialog_data"]["role"]),
    Format("<b>🆔 Телеграм ID:</b> <code>{profile_card[user_id]}</code>"),
    Format("<b>💁🏼‍♂️ Ім'я: </b>{profile_card[full_name]}"),
    Case(
        {
            ...: Format("<b>🪪 Телеграм тег:</b> @{profile_card[username]}"),
            None: Const("<b>🪪 Телеграм тег:</b> <i>відсутній</i>"),
        },
        selector=F["profile_card"]["username"],
    ),
    Case(
        {
            ...: Format(
                "<b>📞 Номер телефону:</b> {profile_card[phone_number]}"
            ),
            None: Const("<b>📞 Номер телефону:</b> <i>відсутній</i>"),
        },
        selector=F["profile_card"]["phone_number"],
    ),
    Case(
        {
            ...: Format("<b>📍 Адреса:</b> {profile_card[address]}"),
            None: Const("<b>📍 Адреса:</b> <i>відсутня</i>"),
        },
        selector=F["profile_card"]["address"],
    ),
)
