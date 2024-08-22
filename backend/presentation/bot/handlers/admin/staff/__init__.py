from aiogram import Dispatcher
from .staff import router as staff_router, staff_workflow_dialog
from .add_to_staff.dialog import add_to_staff_dialog


def setup_staff_workflow_handlers(dp: Dispatcher):
    dp.include_router(staff_router)
    dp.include_router(staff_workflow_dialog)
    dp.include_router(add_to_staff_dialog)


__all__ = [
    "setup_staff_workflow_handlers"
]
