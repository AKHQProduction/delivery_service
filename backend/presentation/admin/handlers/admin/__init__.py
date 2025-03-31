from aiogram import Dispatcher

from .employee import (
    setup_employee_workflow_dialogs,
    setup_employee_workflow_handlers,
)
from .goods import setup_good_workflow_dialogs, setup_good_workflow_handlers
from .profiles import (
    setup_profile_workflow_dialogs,
    setup_profile_workflow_handlers,
)


def setup_admin_handlers(dp: Dispatcher):
    setup_employee_workflow_handlers(dp)
    setup_profile_workflow_handlers(dp)
    setup_good_workflow_handlers(dp)


def setup_admin_dialogs(dp: Dispatcher):
    setup_employee_workflow_dialogs(dp)
    setup_profile_workflow_dialogs(dp)
    setup_good_workflow_dialogs(dp)


__all__ = ["setup_admin_handlers", "setup_admin_dialogs"]
