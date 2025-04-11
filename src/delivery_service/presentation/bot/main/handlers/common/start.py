from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.bot_start import BotStartRequest

START_ROUTER = Router()


@START_ROUTER.message(CommandStart())
async def cmd_start_handler(_: Message, sender: FromDishka[Sender]) -> None:
    await sender.send(BotStartRequest())
