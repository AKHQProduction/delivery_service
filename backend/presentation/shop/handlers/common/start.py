from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.user.interactors.shop_bot_start import (
    ShopBotStart,
    ShopBotStartInputData,
    UserAddressData,
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
            address=UserAddressData(
                city="Черкаси",
                street="Дахнівська",
                house_number=42,
                apartment_number=None,
                floor=None,
                intercom_code=None,
            ),
        )
    )
