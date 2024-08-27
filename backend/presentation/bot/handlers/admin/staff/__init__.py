from aiogram import Dispatcher

from .delete_user_from_staff.dialog import delete_user_from_staff_dialog
from .staff import router as staff_router, staff_workflow_dialog
from .add_user_to_staff.dialog import add_user_to_staff_dialog
from .view_staff_card.dialog import view_staff_card_dialog


def setup_staff_workflow_handlers(dp: Dispatcher):
    dp.include_router(staff_router)
    dp.include_router(staff_workflow_dialog)
    dp.include_router(add_user_to_staff_dialog)
    dp.include_router(view_staff_card_dialog)
    dp.include_router(delete_user_from_staff_dialog)


__all__ = [
    "setup_staff_workflow_handlers"
]
