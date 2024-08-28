from aiogram import Dispatcher
from . import start, create_order, unsupported
from .create_order import create_order_dialog
from .user import setup_user_handlers, profile
from .admin import (
    setup_admin_dialogs,
    setup_admin_handlers
)


def register_handlers(dp: Dispatcher):
    dp.include_routers(start.router)
    dp.include_router(profile.router)
    setup_admin_handlers(dp)

    dp.include_router(unsupported.router)


def register_dialogs(dp: Dispatcher):
    setup_admin_dialogs(dp)


def setup_all(dp: Dispatcher):
    register_handlers(dp)
    register_dialogs(dp)
