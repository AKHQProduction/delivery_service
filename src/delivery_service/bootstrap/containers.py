import logging

from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from delivery_service.bootstrap.configs import (
    DatabaseConfig,
    RabbitConfig,
    RedisConfig,
    TGConfig,
)
from delivery_service.bootstrap.providers import (
    AppConfigProvider,
    ApplicationHandlersProvider,
    ApplicationProvider,
    BazarioProvider,
    DomainProvider,
    GeopyProvider,
    InfrastructureAdaptersProvider,
    PersistenceProvider,
    TelegramProvider,
)

logger = logging.getLogger(__name__)


def bot_container(
    tg_config: TGConfig,
    database_config: DatabaseConfig,
    redis_config: RedisConfig,
    rabbit_config: RabbitConfig,
) -> AsyncContainer:
    logger.info("Bot DI setup")

    return make_async_container(
        AiogramProvider(),
        AppConfigProvider(),
        ApplicationProvider(),
        ApplicationHandlersProvider(),
        BazarioProvider(),
        DomainProvider(),
        GeopyProvider(),
        InfrastructureAdaptersProvider(),
        TelegramProvider(),
        PersistenceProvider(),
        context={
            TGConfig: tg_config,
            DatabaseConfig: database_config,
            RedisConfig: redis_config,
            RabbitConfig: rabbit_config,
        },
    )


def taskiq_container(
    tg_config: TGConfig,
    database_config: DatabaseConfig,
    redis_config: RedisConfig,
    rabbit_config: RabbitConfig,
) -> AsyncContainer:
    logger.info("Taskiq DI setup")

    return make_async_container(
        AppConfigProvider(),
        PersistenceProvider(),
        InfrastructureAdaptersProvider(),
        context={
            TGConfig: tg_config,
            DatabaseConfig: database_config,
            RedisConfig: redis_config,
            RabbitConfig: rabbit_config,
        },
    )
