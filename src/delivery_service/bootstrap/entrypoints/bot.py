import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)
from aiohttp import web

from delivery_service.bootstrap.configs import (
    RedisConfig,
    TGConfig,
    WebhookConfig,
    load_bot_config,
    load_redis_config,
    load_webhook_config,
)
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


def get_admin_dispatcher(storage: BaseStorage) -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=storage)
    setup_all_main_bot_updates(dp)
    logger.debug("Setup admin bot dispatcher")

    return dp


def get_shop_dispatcher(storage: BaseStorage) -> Dispatcher:
    dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=storage)
    logger.debug("Setup shop bot dispatcher")

    return dp


async def on_startup(admin_bot: Bot, webhook_config: WebhookConfig) -> None:
    await admin_bot.delete_webhook(drop_pending_updates=True)
    await admin_bot.set_webhook(
        f"{webhook_config.webhook_url}{webhook_config.webhook_admin_path}"
    )


def main() -> None:
    setup_logging(level="INFO")

    bot_config = load_bot_config()
    webhook_config = load_webhook_config()
    redis_config = load_redis_config()

    session = AiohttpSession()

    bot_settings = {
        "session": session,
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML),
    }

    admin_bot = Bot(token=bot_config.admin_bot_token, **bot_settings)
    storage = get_storage(bot_config=bot_config, redis_config=redis_config)

    admin_dp = get_admin_dispatcher(storage=storage)
    shop_dp = get_shop_dispatcher(storage=storage)

    admin_request_handler = SimpleRequestHandler(admin_dp, admin_bot)

    app = web.Application()
    admin_request_handler.register(app, path=webhook_config.webhook_admin_path)

    TokenBasedRequestHandler(shop_dp, bot_settings=bot_settings).register(
        app, path=webhook_config.webhook_shop_path
    )
    admin_dp.startup.register(on_startup)

    setup_application(
        app, admin_dp, admin_bot=admin_bot, webhook_config=webhook_config
    )
    setup_application(app, shop_dp)

    logger.info("Setup app")
    web.run_app(
        app, host=webhook_config.webhook_host, port=webhook_config.webhook_port
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot was turned off")
