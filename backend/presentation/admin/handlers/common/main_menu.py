from aiogram import F, Router
from aiogram.types import Message

from presentation.admin.consts import FAQ_BTN_TXT

router = Router()


@router.message(F.text == FAQ_BTN_TXT)
async def faq_btn_handler(msg: Message):
    await msg.answer("Тестовый магазин - @SomeTest_robot")
