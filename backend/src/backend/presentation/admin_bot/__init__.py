import logging

from aiogram import Dispatcher

from backend.presentation.admin_bot.dialogs import setup_admin_bot_dialogs
from backend.presentation.admin_bot.handlers import setup_admin_bot_handlers

logger = logging.getLogger(__name__)


def setup_all_admin_bot_handlers(dp: Dispatcher) -> None:
    setup_admin_bot_handlers(dp)
    setup_admin_bot_dialogs(dp)

    logger.debug("Setup all admin bot handlers")
