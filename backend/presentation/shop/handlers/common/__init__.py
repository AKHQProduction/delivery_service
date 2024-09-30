from aiogram import Dispatcher

from . import start


def setup_common_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
