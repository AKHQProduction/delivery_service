from aiogram import Dispatcher

from .view import profile_workflow_dialog, router


def setup_profile_workflow_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


def setup_profile_workflow_dialogs(dp: Dispatcher) -> None:
    dp.include_router(profile_workflow_dialog)


__all__ = ["setup_profile_workflow_handlers", "setup_profile_workflow_dialogs"]
