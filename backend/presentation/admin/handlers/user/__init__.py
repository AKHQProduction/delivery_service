from aiogram import Dispatcher

from .profile import router as profile_router


def setup_user_handlers(dp: Dispatcher) -> None:
    dp.include_router(profile_router)


__all__ = ["setup_user_handlers"]
