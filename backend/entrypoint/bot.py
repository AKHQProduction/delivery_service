import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from dishka.integrations.aiogram import setup_dishka

from entrypoint.config import Config, load_config
from infrastructure.bootstrap.di import setup_di
from presentation.bot.handlers.setup import register_handlers, register_dialogs


def get_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    setup_dishka(container=setup_di(), router=dp, auto_inject=True)

    register_handlers(dp)
    register_dialogs(dp)

    setup_dialogs(dp)

    return dp


async def main():
    logging.basicConfig(level=logging.INFO)

    config: Config = load_config()

    bot = Bot(config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )

    await get_dispatcher().start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
