import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka as add_container_to_bot

from delivery_service.bootstrap.configs import (
    RedisConfig,
    TGConfig,
    WebhookConfig,
    load_bot_config,
    load_database_config,
    load_rabbit_config,
    load_redis_config,
)
from delivery_service.bootstrap.containers import bot_container
from delivery_service.bootstrap.logging import setup_logging
from delivery_service.presentation.bot.main.handlers import (
    setup_all_main_bot_updates,
)

logger = logging.getLogger(__name__)


def get_storage(
    bot_config: TGConfig, redis_config: RedisConfig
) -> BaseStorage:
    if bot_config.use_redis_storage:
        logger.debug("Setup redis storage")
        return RedisStorage.from_url(
            url=redis_config.fsm_uri,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    logger.debug("Setup memory storage")
    return MemoryStorage()


def get_admin_dispatcher(
    storage: BaseStorage, dishka_container: AsyncContainer
) -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=storage)

    add_container_to_bot(dishka_container, router=dp, auto_inject=True)
    setup_all_main_bot_updates(dp)
    setup_dialogs(dp)

    logger.debug("Setup admin bot dispatcher")

    return dp


def get_shop_dispatcher(
    storage: BaseStorage, dishka_container: AsyncContainer
) -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=storage)
    add_container_to_bot(dishka_container, router=dp, auto_inject=True)
    logger.debug("Setup shop bot dispatcher")

    return dp


async def on_startup(admin_bot: Bot, webhook_config: WebhookConfig) -> None:
    await admin_bot.delete_webhook(drop_pending_updates=True)
    await admin_bot.set_webhook(
        f"{webhook_config.webhook_url}{webhook_config.webhook_admin_path}"
    )


async def main() -> None:
    setup_logging(level="INFO")

    bot_config = load_bot_config()
    redis_config = load_redis_config()
    database_config = load_database_config()
    rabbit_config = load_rabbit_config()

    dishka_container = bot_container(
        tg_config=bot_config,
        redis_config=redis_config,
        database_config=database_config,
        rabbit_config=rabbit_config,
    )

    bot = Bot(
        token=bot_config.admin_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = get_admin_dispatcher(
        storage=get_storage(bot_config=bot_config, redis_config=redis_config),
        dishka_container=dishka_container,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot was turned off")
