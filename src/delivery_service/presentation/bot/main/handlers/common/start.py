from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

START_ROUTER = Router()


@START_ROUTER.message(CommandStart())
async def cmd_start_handler(msg: Message) -> None:
    await msg.answer("Hello, user!")
