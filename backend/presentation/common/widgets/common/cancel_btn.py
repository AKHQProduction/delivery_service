from aiogram import Bot, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import MagicFilter

from application.common.identity_provider import IdentityProvider
from application.user.commands.admin_bot_start import (
    AdminBotStartCommandHandler,
)
from presentation.admin.handlers.common.start import cmd_start

dialog_has_mistakes_in_input = F["dialog_data"]["input_has_mistake"]


def setup_input_error_flag(manager: DialogManager, flag: bool) -> None:
    manager.dialog_data["input_has_mistake"] = flag


@inject
async def handle_back_to_main_menu_btn(
    call: CallbackQuery,
    _: Button,
    manager: DialogManager,
    action: FromDishka[AdminBotStartCommandHandler],
    id_provider: FromDishka[IdentityProvider],
) -> None:
    bot: Bot = manager.middleware_data["bot"]

    await manager.done()
    await call.message.delete()
    await cmd_start(call, bot, action, id_provider)


def back_to_main_menu_btn(
    btn_txt: str, when: str | MagicFilter | None = None
) -> Button:
    return Button(
        text=Const(btn_txt),
        on_click=handle_back_to_main_menu_btn,  # noqa: ignore
        id="back_to_main_menu_btn",
        when=when,
    )
