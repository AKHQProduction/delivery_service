import logging

from dishka import AsyncContainer, make_async_container

from delivery_service.bootstrap.configs import (
    DatabaseConfig,
    RedisConfig,
    TGConfig,
)
from delivery_service.bootstrap.providers import (
    AppConfigProvider,
    ApplicationHandlersProvider,
    ApplicationProvider,
    BazarioProvider,
    DomainProvider,
    InfrastructureAdaptersProvider,
    PersistenceProvider,
    TelegramProvider,
)

logger = logging.getLogger(__name__)


def bot_container(
    tg_config: TGConfig,
    database_config: DatabaseConfig,
    redis_config: RedisConfig,
) -> AsyncContainer:
    logger.info("DI setup")
    return make_async_container(
        AppConfigProvider(),
        ApplicationProvider(),
        ApplicationHandlersProvider(),
        BazarioProvider(),
        DomainProvider(),
        InfrastructureAdaptersProvider(),
        TelegramProvider(),
        PersistenceProvider(),
        context={
            TGConfig: tg_config,
            DatabaseConfig: database_config,
            RedisConfig: redis_config,
        },
    )
