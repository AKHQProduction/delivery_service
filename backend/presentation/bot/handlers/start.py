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
):
    user_id: int = msg.from_user.id
    full_name: str = msg.from_user.full_name
    username: str | None = msg.from_user.username

    await action(
            BotStartDTO(
                user_id=user_id,
                full_name=full_name,
                username=username
                )
    )

    await msg.answer(
            text=f"Hello, {full_name}",
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
