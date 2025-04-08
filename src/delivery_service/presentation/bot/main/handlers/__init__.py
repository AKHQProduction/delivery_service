import logging

from aiogram import Dispatcher

from delivery_service.presentation.bot.main.handlers.common import (
    setup_common_handlers,
)
from delivery_service.presentation.bot.main.handlers.user import (
    setup_user_dialogs,
    setup_user_handlers,
)

logger = logging.getLogger(__name__)


def setup_all_handlers(dp: Dispatcher) -> None:
    setup_common_handlers(dp)
    setup_user_handlers(dp)


def setup_all_dialogs(dp: Dispatcher) -> None:
    setup_user_dialogs(dp)


def setup_all_main_bot_updates(dp: Dispatcher) -> None:
    setup_all_handlers(dp)
    setup_all_dialogs(dp)

    logger.debug("Setup all main bot updates")
