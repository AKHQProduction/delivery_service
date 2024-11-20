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
from aiogram_dialog import setup_dialogs
from aiohttp import web
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from application.shop.interactors.setup_all_shops import SetupAllShop
from entrypoint.config import Config, load_config
from infrastructure.bootstrap.di import setup_di
from infrastructure.persistence.models import map_tables
from presentation.admin.handlers.setup import setup_all_admin_bot_handlers
from presentation.common.widgets.common.message_manager import (
    CustomMessageManager,
)
from presentation.shop.handlers.setup import setup_all_shop_bot_handlers
from presentation.shop.middlewares import setup_shop_bot_middlewares


def get_storage(config: Config) -> BaseStorage:
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    return MemoryStorage()


def get_admin_dispatcher(
    container: AsyncContainer, config: Config
) -> Dispatcher:
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(), storage=get_storage(config)
    )

    setup_dishka(container=container, router=dp, auto_inject=True)

    # Setup handlers and dialogs
    setup_all_admin_bot_handlers(dp)

    setup_dialogs(dp, message_manager=CustomMessageManager(container))

    return dp


def get_shop_dispatcher(
    container: AsyncContainer, config: Config
) -> Dispatcher:
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(), storage=get_storage(config)
    )

    setup_shop_bot_middlewares(dp)

    setup_dishka(container=container, router=dp, auto_inject=True)

    # Setup handlers and dialogs
    setup_all_shop_bot_handlers(dp)

    setup_dialogs(dp, message_manager=CustomMessageManager(container))

    return dp


async def on_startup(
    bot: Bot, config: Config, container: AsyncContainer
) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        f"{config.webhook.webhook_url}{config.webhook.webhook_admin_path}",
    )

    async with container() as containers:
        setup_all_bots = await containers.get(SetupAllShop)

        await setup_all_bots()


def main():
    logging.basicConfig(level=logging.INFO)

    container = setup_di()  # Dishka containers

    config = load_config()
    session = AiohttpSession()

    bot_settings = {
        "session": session,
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML),
    }

    admin_bot = Bot(token=config.tg_bot.admin_bot_token, **bot_settings)

    admin_dp = get_admin_dispatcher(container, config)
    shop_dp = get_shop_dispatcher(container, config)

    admin_request_handler = SimpleRequestHandler(admin_dp, admin_bot)

    app = web.Application()
    admin_request_handler.register(app, path=config.webhook.webhook_admin_path)

    TokenBasedRequestHandler(shop_dp, bot_settings=bot_settings).register(
        app,
        path=config.webhook.webhook_shop_path,
    )

    admin_dp.startup.register(on_startup)

    setup_application(
        app, admin_dp, bot=admin_bot, config=config, container=container
    )
    setup_application(app, shop_dp)

    map_tables()

    web.run_app(
        app, host=config.webhook.webhook_host, port=config.webhook.webhook_port
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.exception("Бот був вимкнений!")
