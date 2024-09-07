from dataclasses import asdict
from typing import Any

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.user.interactors.get_user import (
    GetUser,
    GetUserRequestData,
    UserResponseData
)


@inject
async def get_user_getter(
        dialog_manager: DialogManager,
        action: FromDishka[GetUser],
        **_kwargs
) -> dict[str, Any]:
    user_id = dialog_manager.dialog_data["user_id"]

    user: UserResponseData = await action(GetUserRequestData(user_id=user_id))

    return {
        "user": asdict(user)
    }
