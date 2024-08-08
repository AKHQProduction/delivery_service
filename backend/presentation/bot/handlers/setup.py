from aiogram import Dispatcher
from presentation.bot.handlers import start


def setup_handlers(dp: Dispatcher):
    dp.include_routers(start.router)
