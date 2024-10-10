from aiogram import F, Router
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Const

from presentation.admin.handlers.user.profile import states
from presentation.common.consts import PROFILE_BTN_TXT
from presentation.common.helpers import default_on_start_handler
from presentation.common.widgets.user.profile_card import (
    get_profile_card,
    profile_card,
)

router = Router()


@router.message(F.text == PROFILE_BTN_TXT)
async def profile_handler(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.ProfileMainMenu.MAIN, mode=StartMode.RESET_STACK
    )


profile_in_admin_bot_dialog = Dialog(
    Window(
        profile_card,
        Row(
            Start(
                id="change_phone_number_in_profile",
                text=Const("Змінити телефон"),
                state=states.ProfileChangePhone.NEW_PHONE,
            ),
            Start(
                id="change_address_in_profile",
                text=Const("Змінити адресу"),
                state=states.ProfileChangeAddress.NEW_ADDRESS,
            ),
        ),
        state=states.ProfileMainMenu.MAIN,
        getter=get_profile_card,
    ),
    on_start=default_on_start_handler,
)
