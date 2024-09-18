from aiogram import Dispatcher

from .admin import setup_admin_dialogs, setup_admin_handlers
from .common import setup_common_handlers
from .user import profile


def register_handlers(dp: Dispatcher):
    dp.include_router(profile.router)
    setup_admin_handlers(dp)

    # Always must be last registered
    setup_common_handlers(dp)


def register_dialogs(dp: Dispatcher):
    setup_admin_dialogs(dp)


def setup_all(dp: Dispatcher):
    register_handlers(dp)
    register_dialogs(dp)
