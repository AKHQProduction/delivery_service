from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.user.interactors.shop_bot_start import (
    ShopBotStart,
    ShopBotStartInputData,
)

router = Router()


@router.message(CommandStart())
async def shop_cmd_start(
    msg: Message, bot: Bot, action: FromDishka[ShopBotStart]
):
    shop_id = bot.id

    await action(
        data=ShopBotStartInputData(
            shop_id=shop_id,
            user_id=msg.from_user.id,
            full_name=msg.from_user.full_name,
            username=msg.from_user.username,
        )
    )
