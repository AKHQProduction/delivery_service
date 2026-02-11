import logging
from collections.abc import AsyncIterable, AsyncIterator

from dishka import (
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

from backend.bootstrap.config import (
    AppConfig,
    Config,
    OSRMConfig,
    OTelConfig,
    PostgresConfig,
    RedisConfig,
    TelegramConfig,
    WebhookConfig,
)
from backend.infrastructure.persistence.gateways import (
    RedisLinkGateway,
    RedisPDFStorage,
    SQLAlchemyCategoryGateway,
    SQLAlchemyClientGateway,
    SQLAlchemyDistrictGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

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

    @provide
    def webhook_config(self, config: Config) -> WebhookConfig:
        return config.webhook_config

    @provide
    def otel_config(self, config: Config) -> OTelConfig:
        return config.otel_config

    @provide
    def osrm_config(self, config: Config) -> OSRMConfig:
        return config.osrm_config


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(
        self, config: PostgresConfig
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            config.uri,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
        )

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
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session

    @provide
    def transaction_manager(self, session: AsyncSession) -> TransactionManager:
        return TransactionManager(session)

    gateways = provide_all(
        SQLAlchemyUserGateway,
        SQLAlchemyShopGateway,
        SQLAlchemyProductGateway,
        SQLAlchemyCategoryGateway,
        SQLAlchemyDistrictGateway,
        SQLAlchemyClientGateway,
        SQLAlchemyOrderGateway,
        SQLAlchemyTimeSlotGateway,
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
    pdf_storage = provide(RedisPDFStorage)
