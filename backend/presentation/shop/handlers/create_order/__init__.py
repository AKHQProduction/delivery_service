from aiogram import Dispatcher

from .create_order import create_order_dialog
from .select_goods_to_cart import router, select_goods_dialog


def setup_create_order_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


def setup_create_order_dialogs(dp: Dispatcher) -> None:
    dp.include_router(select_goods_dialog)
    dp.include_router(create_order_dialog)
