import logging

from aiogram import Dispatcher

from .new_shop import new_shop_dialog

logger = logging.getLogger(__name__)


def setup_admin_bot_dialogs(dp: Dispatcher) -> None:
    dp.include_router(new_shop_dialog)

    logger.debug("Setup admin bot dialogs")
