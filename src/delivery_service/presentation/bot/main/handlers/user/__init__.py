from aiogram import Dispatcher

from .create_shop import CREATE_SHOP_ROUTER, SHOP_CREATION_DIALOG


def setup_user_handlers(dp: Dispatcher) -> None:
    dp.include_router(CREATE_SHOP_ROUTER)


def setup_user_dialogs(dp: Dispatcher) -> None:
    dp.include_router(SHOP_CREATION_DIALOG)
