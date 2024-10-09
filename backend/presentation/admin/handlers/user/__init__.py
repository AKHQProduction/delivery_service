from aiogram import Dispatcher

from .create_shop.dialog import create_shop_dialog
from .create_shop.dialog import router as create_shop_router
from .profile.change_phone import change_phone_dialog
from .profile.main import profile_in_admin_bot_dialog
from .profile.main import router as profile_router


def setup_user_handlers(dp: Dispatcher) -> None:
    dp.include_router(create_shop_router)
    dp.include_router(profile_router)


def setup_user_dialogs(dp: Dispatcher) -> None:
    dp.include_router(create_shop_dialog)
    dp.include_router(profile_in_admin_bot_dialog)
    dp.include_router(change_phone_dialog)


__all__ = ["setup_user_handlers", "setup_user_dialogs"]
