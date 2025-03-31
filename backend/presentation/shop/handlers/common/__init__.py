from aiogram import Dispatcher

from . import start, unsupported


def setup_common_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(unsupported.router)
