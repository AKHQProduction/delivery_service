from aiogram import Dispatcher

from .main import create_shop_dialog
from .main import router as main_router


def setup_create_shop_handlers(dp: Dispatcher) -> None:
    dp.include_router(main_router)


def setup_create_shop_dialogs(dp: Dispatcher) -> None:
    dp.include_router(create_shop_dialog)
