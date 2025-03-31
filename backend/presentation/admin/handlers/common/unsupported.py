import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command(commands=re.compile(".*")))
async def unsupported_commands(msg: Message):
    await msg.answer("Вибачте, такой команди не існує")
