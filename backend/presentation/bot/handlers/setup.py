from aiogram import Dispatcher
from . import start, create_order
from .create_order import create_order_dialog
from .user import setup_user_handlers
from .admin import setup_admin_handlers


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        start.router,
    )

    setup_user_handlers(dp)
    setup_admin_handlers(dp)


def register_dialogs(dp: Dispatcher):
    dp.include_router(create_order_dialog)
