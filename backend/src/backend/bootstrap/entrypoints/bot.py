import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs

from backend.bootstrap.config import Config
from backend.bootstrap.logger import setup_logging
from backend.presentation.admin_bot import setup_all_admin_bot_handlers

logger = logging.getLogger(__name__)


def get_storage(config: Config) -> BaseStorage:
    if config.telegram_config.use_redis:
        logger.debug("Setup redis storage for bot fsm")
        return RedisStorage.from_url(url="sss")
    logger.debug("Setup in-memory storage for bot fsm")
    return MemoryStorage()


async def main() -> None:
    config = Config()
    setup_logging(level="DEBUG" if config.app_config.debug else "INFO")

    bot = Bot(
        token=config.telegram_config.admin_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(), storage=get_storage(config)
    )

    setup_all_admin_bot_handlers(dp)
    setup_dialogs(dp)
    logger.debug("Setup admin bot")

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot was turned off")
