from aiogram import Dispatcher
from . import start


def setup_handlers(dp: Dispatcher):
    dp.include_routers(start.router)
