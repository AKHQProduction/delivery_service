from aiogram import Dispatcher

from .good import (
    setup_good_workflow_handlers,
    setup_good_workflow_dialogs
)
from .staff import (
    setup_staff_workflow_dialogs,
    setup_staff_workflow_handlers
)


def setup_admin_handlers(dp: Dispatcher):
    setup_staff_workflow_handlers(dp)
    setup_good_workflow_handlers(dp)


def setup_admin_dialogs(dp: Dispatcher):
    setup_staff_workflow_dialogs(dp)
    setup_good_workflow_dialogs(dp)


__all__ = [
    "setup_admin_handlers",
    "setup_admin_dialogs"
]
