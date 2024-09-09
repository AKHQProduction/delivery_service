import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler, setup_application
)
from aiogram_dialog import setup_dialogs
from aiohttp import web
from dishka.integrations.aiogram import setup_dishka

from entrypoint.config import Config, load_config
from infrastructure.bootstrap.di import setup_di
from infrastructure.persistence.models import map_tables
from infrastructure.tg.bot_webhook_manager import BotWebhookManager
from presentation.admin.handlers.setup import setup_all


def get_admin_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    setup_dishka(container=setup_di(), router=dp, auto_inject=True)

    setup_all(dp)

    setup_dialogs(dp)

    return dp


def get_shop_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    return dp


async def on_startup_admin_bot(
        bot: Bot, config: Config, shop_bot_token: str
) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
            f"{config.webhook.webhook_url}{config.webhook.webhook_admin_path}"
    )

    await BotWebhookManager(
            config.webhook
    ).setup_webhook(
            config.tg_bot.shop_bot_token
    )


async def add_shop_bot(bot: Bot, new_bot_token: str, config: Config):
    new_bot = Bot(token=new_bot_token, session=bot.session)

    try:
        await new_bot.get_me()
    except TelegramUnauthorizedError as err:
        print(err)

    await new_bot.delete_webhook(drop_pending_updates=True)

    webhook_shop_path = config.webhook.webhook_shop_path.format(
            bot_token=new_bot_token
    )

    await new_bot.set_webhook(
            f"{config.webhook.webhook_url}"
            f"{webhook_shop_path}"
    )


def main():
    logging.basicConfig(level=logging.INFO)

    config: Config = load_config()
    session = AiohttpSession()

    bot_settings = {
        "session": session,
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML)
    }

    admin_bot = Bot(
            token=config.tg_bot.admin_bot_token,
            **bot_settings
    )

    admin_dp = get_admin_dispatcher()
    shop_dp = get_shop_dispatcher()

    admin_request_handler = SimpleRequestHandler(
            admin_dp, admin_bot
    )

    app = web.Application()
    admin_request_handler.register(app, path=config.webhook.webhook_admin_path)

    TokenBasedRequestHandler(
            shop_dp,
            bot_settings=bot_settings
    ).register(app, path=config.webhook.webhook_shop_path)

    admin_dp.startup.register(on_startup_admin_bot)

    setup_application(
            app,
            admin_dp,
            bot=admin_bot,
            config=config,
            shop_bot_token=config.tg_bot.shop_bot_token
    )
    setup_application(app, shop_dp)

    map_tables()

    web.run_app(
            app,
            host=config.webhook.webhook_host,
            port=config.webhook.webhook_port
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот був вимкнений!")
