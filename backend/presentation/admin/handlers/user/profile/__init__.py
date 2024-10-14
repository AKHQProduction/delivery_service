from aiogram import Dispatcher

from .change_address import (
    change_address_dialog,
    other_information_about_address_dialog,
    send_address_by_telegram_dialog,
    send_address_by_user_dialog,
)
from .change_phone import change_phone_number_dialog
from .main import router


def setup_profile_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


def setup_profile_dialogs(dp: Dispatcher) -> None:
    dp.include_router(change_phone_number_dialog)
    dp.include_router(change_address_dialog)
    dp.include_router(send_address_by_telegram_dialog)
    dp.include_router(send_address_by_user_dialog)
    dp.include_router(other_information_about_address_dialog)
