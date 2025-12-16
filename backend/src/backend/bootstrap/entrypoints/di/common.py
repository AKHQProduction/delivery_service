import logging
from collections.abc import AsyncIterable, AsyncIterator

from dishka import (
    AnyOf,
    Provider,
    Scope,
    WithParents,
    from_context,
    provide,
    provide_all,
)
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application.interfaces import TransactionManager
from backend.bootstrap.config import (
    AppConfig,
    Config,
    PostgresConfig,
    RedisConfig,
    TelegramConfig,
)
from backend.infrastructure.persistence.gateways import (
    RedisLinkGateway,
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.persistence.gateways.product_gateway import (
    SQLAlchemyProductGateway,
)

logger = logging.getLogger(__name__)


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(Config)

    @provide
    def app_config(self, config: Config) -> AppConfig:
        return config.app_config

    @provide
    def telegram_config(self, config: Config) -> TelegramConfig:
        return config.telegram_config

    @provide
    def redis_config(self, config: Config) -> RedisConfig:
        return config.redis_config

    @provide
    def postgres_config(self, config: Config) -> PostgresConfig:
        return config.postgres_config


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(
        self, config: PostgresConfig
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(config.uri)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )
        logger.debug("Session provider was initialized")
        return factory

    @provide
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AnyOf[AsyncSession, TransactionManager]]:
        async with factory() as session:
            yield session

    gateways = provide_all(
        WithParents[SQLAlchemyUserGateway],
        WithParents[SQLAlchemyShopGateway],
        WithParents[SQLAlchemyProductGateway],
        WithParents[SQLAlchemyClientGateway],
        WithParents[SQLAlchemyOrderGateway],
    )


class RedisProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def redis_session(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(
            config.persistence_uri, decode_responses=True
        ) as redis:
            yield redis

    gateway = provide(WithParents[RedisLinkGateway])
