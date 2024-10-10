import re
from typing import Any

from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram_dialog import DialogManager

from application.common.identity_provider import IdentityProvider
from presentation.admin.keyboards.main_menu_kb import MainReplyKeyboard


async def step_toggler_in_form(
    manager: DialogManager, key: str, state: State
) -> None:
    flag = manager.dialog_data.get(key, False)

    await manager.switch_to(state=state) if flag else await manager.next()


async def default_on_start_handler(
    data: dict[str, Any], manager: DialogManager
) -> None:
    if data:
        manager.dialog_data.update(data)


async def send_main_keyboard(
    manager: DialogManager, text: str, id_provider: IdentityProvider
) -> Message:
    bot: Bot = manager.middleware_data["bot"]
    role = await id_provider.get_role()

    msg = await bot.send_message(
        chat_id=manager.event.from_user.id,
        text=text,
        reply_markup=await MainReplyKeyboard(role).render_keyboard(),
    )

    return msg


def parse_address(address: str) -> dict[str, Any]:
    pattern = (
        r"(?P<city>[^,]+),\s(?P<street>[^\d]+)\s(?P<house_number>\d+(/\d+)?)"
    )
    match = re.match(pattern, address)

    return match.groupdict()
