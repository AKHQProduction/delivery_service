import logging

from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider

from backend.bootstrap.config import Config
from backend.bootstrap.entrypoints.di.api_providers import (
    APIInteractorsProvider,
    WebAppProvider,
)
from backend.bootstrap.entrypoints.di.bot_providers import (
    BotInteractorsProvider,
    TelegramProvider,
)
from backend.bootstrap.entrypoints.di.common import (
    ConfigProvider,
    PersistenceProvider,
    RedisProvider,
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


def api_container(config: Config) -> AsyncContainer:
    logger.info("Setup api container")

    return make_async_container(
        ConfigProvider(),
        FastapiProvider(),
        PersistenceProvider(),
        RedisProvider(),
        WebAppProvider(),
        APIInteractorsProvider(),
        context={Config: config},
    )
