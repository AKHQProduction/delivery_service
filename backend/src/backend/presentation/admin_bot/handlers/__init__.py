import logging

from aiogram import Dispatcher

from backend.presentation.admin_bot.handlers.user import setup_user_handlers

logger = logging.getLogger(__name__)


def setup_admin_bot_handlers(dp: Dispatcher) -> None:
    setup_user_handlers(dp)

    logger.debug("Setup admin bot handlers")
