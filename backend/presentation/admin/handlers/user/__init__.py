from aiogram import Dispatcher

from .create_shop import setup_create_shop_dialogs, setup_create_shop_handlers
from .profile import setup_profile_dialogs, setup_profile_handlers


def setup_user_handlers(dp: Dispatcher) -> None:
    setup_create_shop_handlers(dp)
    setup_profile_handlers(dp)


def setup_user_dialogs(dp: Dispatcher) -> None:
    setup_profile_dialogs(dp)
    setup_create_shop_dialogs(dp)


__all__ = ["setup_user_handlers", "setup_user_dialogs"]
