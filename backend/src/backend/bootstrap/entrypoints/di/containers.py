import logging

from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from backend.bootstrap.config import Config
from backend.bootstrap.entrypoints.di.bot_providers import (
    BotInteractorsProvider,
    ConfigProvider,
    PersistenceProvider,
    RedisProvider,
    TelegramProvider,
)

logger = logging.getLogger(__name__)


def bot_container(config: Config) -> AsyncContainer:
    logger.info("Setup bot container")

    return make_async_container(
        AiogramProvider(),
        ConfigProvider(),
        BotInteractorsProvider(),
        TelegramProvider(),
        PersistenceProvider(),
        RedisProvider(),
        context={Config: config},
    )
