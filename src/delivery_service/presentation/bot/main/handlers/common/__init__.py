from aiogram import Dispatcher

from .start import START_ROUTER


def setup_common_handlers(dp: Dispatcher) -> None:
    dp.include_router(START_ROUTER)
