from typing import Any, cast

from aiogram import Bot
from aiogram.types import Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from backend.application.commands import (
    CreateShopCommand,
    CreateShopCommandHandler,
)
from backend.presentation.admin_bot import states
from backend.presentation.admin_bot.keyboards.inline import shop_kb


@inject
async def on_input_shp_name(
    _: Message,
    __: Any,
    manager: DialogManager,
    value: str,
    handler: FromDishka[CreateShopCommandHandler],
) -> None:
    bot: Bot = cast("Bot", manager.middleware_data.get("bot"))
    user: User = cast("User", manager.middleware_data.get("event_from_user"))

    await handler.handle(
        CreateShopCommand(name=value, owner_full_name=user.full_name)
    )

    bot_info = await bot.get_me()
    await bot.send_message(
        chat_id=user.id,
        text=f"🙋 З поверненням, {user.first_name}!",
        reply_markup=shop_kb(cast("str", bot_info.username)),
    )
    await manager.done()


new_shop_dialog = Dialog(
    Window(
        Const("🙋 Привіт, для початку роботи введіть назву магазину"),
        TextInput(id="i_shop_name", on_success=on_input_shp_name),
        state=states.NewShop.NAME,
    )
)
