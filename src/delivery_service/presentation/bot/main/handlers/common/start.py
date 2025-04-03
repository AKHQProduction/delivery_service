from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.bot_start import BotStartRequest
from delivery_service.domain.staff.repository import TelegramContactsData

START_ROUTER = Router()


@START_ROUTER.message(CommandStart())
async def cmd_start_handler(msg: Message, sender: FromDishka[Sender]) -> None:
    if not msg.from_user:
        return

    await sender.send(
        BotStartRequest(
            full_name=msg.from_user.full_name,
            telegram_data=TelegramContactsData(
                telegram_id=msg.from_user.id,
                telegram_username=msg.from_user.username,
            ),
        )
    )

    await msg.answer("Hello, user!")
