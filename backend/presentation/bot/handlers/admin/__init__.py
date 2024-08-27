from aiogram import Dispatcher

from .staff import setup_staff_workflow_handlers


def setup_admin_handlers(dp: Dispatcher):
    setup_staff_workflow_handlers(dp)


__all__ = [
    "setup_admin_handlers"
]
