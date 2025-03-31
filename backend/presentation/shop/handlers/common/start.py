from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.commands.bot.shop_bot_start import (
    ShopBotStart,
    ShopBotStartInputData,
)
from presentation.shop.main_keyboard import main_menu_shop_bot

router = Router()


@router.message(CommandStart())
async def shop_cmd_start(
    msg: Message, shop_id: int, action: FromDishka[ShopBotStart]
):
    name = msg.from_user.full_name

    await action(
        data=ShopBotStartInputData(
            shop_id=shop_id,
            tg_id=msg.from_user.id,
            full_name=name,
            username=msg.from_user.username,
        )
    )

    await msg.answer(f"Hello, {name}!", reply_markup=main_menu_shop_bot())
