from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const

from presentation.common.consts import GOODS_BTN_TEXT

from . import states

router = Router()


@router.message(Command("goods"))
@router.message(F.text == GOODS_BTN_TEXT)
async def good_workflow_btn(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.GoodWorkflow.MAIN_MENU,
        mode=StartMode.RESET_STACK,
    )


good_workflow_dialog = Dialog(
    Window(Const("Work"), state=states.GoodWorkflow.MAIN_MENU),
)
