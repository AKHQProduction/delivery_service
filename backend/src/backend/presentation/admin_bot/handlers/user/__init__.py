import logging

from aiogram import Dispatcher

from .start import router as start_router

logger = logging.getLogger(__name__)


def setup_user_handlers(dp: Dispatcher) -> None:
    dp.include_router(start_router)

    logger.debug("Setup user handlers")
