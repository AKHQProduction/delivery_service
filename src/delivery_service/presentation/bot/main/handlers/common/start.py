from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.bot_start import BotStartRequest
from delivery_service.application.common.dto import TelegramContactsData
from delivery_service.domain.shared.new_types import Empty

START_ROUTER = Router()


@START_ROUTER.message(CommandStart())
async def cmd_start_handler(msg: Message, sender: FromDishka[Sender]) -> None:
    if not msg.from_user:
        return

    username = (
        msg.from_user.username if msg.from_user.username else Empty.UNSET
    )

    await sender.send(
        BotStartRequest(
            telegram_data=TelegramContactsData(
                full_name=msg.from_user.full_name,
                telegram_id=msg.from_user.id,
                telegram_username=username,
            ),
        )
    )
