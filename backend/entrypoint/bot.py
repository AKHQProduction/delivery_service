import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from backend.entrypoint.config import Config, load_config
from backend.infrastructure.bootstrap.di import setup_di
from backend.presentation.bot.setup import setup_handlers


def get_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    setup_dishka(container=setup_di(), router=dp, auto_inject=True)
    setup_handlers(dp)

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
