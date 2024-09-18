from aiogram import F, Router
from aiogram.types import Message

from presentation.admin.consts import CREATE_NEW_SHOP_TXT

router = Router()


@router.message(F.text == CREATE_NEW_SHOP_TXT)
async def create_new_shop_btn(
    msg: Message,
):
    await msg.answer(CREATE_NEW_SHOP_TXT)
