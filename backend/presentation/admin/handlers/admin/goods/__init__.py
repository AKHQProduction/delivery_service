from aiogram import Dispatcher

from .add import add_new_goods_dialog
from .edit import edit_goods_dialog
from .main import (
    goods_workflow_dialog,
    router,
)
from .view import view_goods_dialog


def setup_good_workflow_handlers(dp: Dispatcher):
    dp.include_router(router)


def setup_good_workflow_dialogs(dp: Dispatcher):
    dp.include_router(goods_workflow_dialog)
    dp.include_router(add_new_goods_dialog)
    dp.include_router(view_goods_dialog)
    dp.include_router(edit_goods_dialog)


__all__ = ["setup_good_workflow_handlers", "setup_good_workflow_dialogs"]
