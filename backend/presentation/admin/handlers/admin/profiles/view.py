from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const

from presentation.common.consts import CLIENTS_BTN_TXT

from . import states

router = Router()


@router.message(F.text == CLIENTS_BTN_TXT)
async def clients_btn_handler(_msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.ProfileMenu.VIEW, mode=StartMode.RESET_STACK
    )


profile_workflow_dialog = Dialog(
    Window(Const("Work"), state=states.ProfileMenu.VIEW)
)
