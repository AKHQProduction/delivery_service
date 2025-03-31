from aiogram import Dispatcher

from .main import router


def setup_profile_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
