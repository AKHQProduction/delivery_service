from aiogram import Dispatcher

from .main.dialog import good_workflow_dialog, router


def setup_good_workflow_handlers(dp: Dispatcher):
    dp.include_router(router)


def setup_good_workflow_dialogs(dp: Dispatcher):
    dp.include_router(good_workflow_dialog)


__all__ = ["setup_good_workflow_handlers", "setup_good_workflow_dialogs"]
