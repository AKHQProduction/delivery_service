import logging

from aiogram import Dispatcher

from delivery_service.presentation.bot.main.handlers.common import (
    setup_common_handlers,
)

logger = logging.getLogger(__name__)


def setup_all_handlers(dp: Dispatcher) -> None:
    setup_common_handlers(dp)


def setup_all_main_bot_updates(dp: Dispatcher) -> None:
    setup_all_handlers(dp)

    logger.debug("Setup all main bot updates")
