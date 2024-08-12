from aiogram import Dispatcher
from . import start, create_order
from .create_order import create_order_dialog


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        start.router,
        create_order.router
    )


def register_dialogs(dp: Dispatcher):
    dp.include_router(create_order_dialog)
