from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, User, ReplyKeyboardMarkup, KeyboardButton
from dishka import FromDishka

from application.bot_start import BotStart, BotStartDTO

router = Router()


@router.message(CommandStart())
async def cmd_start(
        msg: Message,
        action: FromDishka[BotStart],
        user: FromDishka[User]
):
    await action(
        BotStartDTO(user_id=user.id,
                    full_name=user.full_name,
                    username=user.username
                    )
    )

    await msg.answer(
        text=f"Hello, {user.full_name}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🛒 Створити замовлення")
                ],
                [
                    KeyboardButton(text="🗄 Мої замовлення")
                ]
            ],
            resize_keyboard=True
        )
    )
