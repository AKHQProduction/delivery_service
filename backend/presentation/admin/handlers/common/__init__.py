from aiogram import Dispatcher
from . import start, unsupported, main_menu


def setup_common_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(unsupported.router)
    dp.include_router(main_menu.router)
