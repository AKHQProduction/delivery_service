from aiogram import Dispatcher

from presentation.shop.handlers.common import setup_common_handlers
from presentation.shop.handlers.profile import (
    setup_profile_dialogs,
    setup_profile_handlers,
)


def register_handlers(dp: Dispatcher) -> None:
    setup_profile_handlers(dp)
    # Always must be last registered
    setup_common_handlers(dp)


def register_dialogs(dp: Dispatcher) -> None:
    setup_profile_dialogs(dp)


def setup_all_shop_bot_handlers(dp: Dispatcher) -> None:
    register_handlers(dp)
    register_dialogs(dp)
