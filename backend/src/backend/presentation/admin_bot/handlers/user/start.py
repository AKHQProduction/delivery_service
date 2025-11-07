from typing import cast

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message, User
from aiogram_dialog import DialogManager, StartMode

from backend.presentation.admin_bot import states
from backend.presentation.admin_bot.keyboards.inline import shop_kb

router = Router()


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def cmd_start(
    message: Message, dialog_manager: DialogManager
) -> Message | None:
    user: User = cast("User", message.from_user)

    exists = True
    if exists:
        return await message.answer(
            f"🙋 Привіт, {user.first_name}!", reply_markup=shop_kb()
        )
    await dialog_manager.start(
        state=states.NewShop.NAME, mode=StartMode.RESET_STACK
    )
    return None
