from aiogram import Dispatcher

from .create_shop.dialog import create_shop_dialog
from .create_shop.dialog import router as create_shop_router


def setup_user_handlers(dp: Dispatcher) -> None:
    dp.include_router(create_shop_router)


def setup_user_dialogs(dp: Dispatcher) -> None:
    dp.include_router(create_shop_dialog)


__all__ = ["setup_user_handlers", "setup_user_dialogs"]
