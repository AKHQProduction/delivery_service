from aiogram import F, Router
from aiogram.types import Message

from presentation.common.consts import PROFILE_BTN_TXT

router = Router()


@router.message(F.text == PROFILE_BTN_TXT)
async def profile_handler(msg: Message):
    await msg.answer(f"🆔 <code>{msg.from_user.id}</code>")
