from aiogram import Dispatcher

from . import main_menu, start, unsupported


def setup_common_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(unsupported.router)
    dp.include_router(main_menu.router)
