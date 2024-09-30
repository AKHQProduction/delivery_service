from aiogram import Dispatcher

from presentation.shop.handlers.common import setup_common_handlers


def register_handlers(dp: Dispatcher) -> None:
    # Always must be last registered
    setup_common_handlers(dp)


def setup_all_shop_bot_handlers(dp: Dispatcher) -> None:
    register_handlers(dp)
