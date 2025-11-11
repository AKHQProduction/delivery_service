import logging
from collections.abc import AsyncIterable, AsyncIterator
from typing import cast

from aiogram.types import User
from dishka import (
    Provider,
    Scope,
    WithParents,
    from_context,
    provide,
    provide_all,
)
from dishka.integrations.aiogram import AiogramMiddlewareData
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application.commands import (
    BotStartCommandHandler,
    CreateNewShopCommandHandler,
)
from backend.application.interfaces import IdentityProvider
from backend.bootstrap.config import (
    AppConfig,
    Config,
    PostgresConfig,
    RedisConfig,
    TelegramConfig,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.persistence.tr_manager import (
    SQLAlchemyTransactionManager,
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


class BotInteractorsProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(BotStartCommandHandler, CreateNewShopCommandHandler)


class TelegramProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def current_user(self, middleware_data: AiogramMiddlewareData) -> User:
        return cast("User", middleware_data.get("event_from_user"))

    @provide
    def idp(
        self, user: "User", user_gateway: SQLAlchemyUserGateway
    ) -> IdentityProvider:
        return TelegramIdentityProvider(
            telegram_id=user.id, user_gateway=user_gateway
        )


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
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session

    gateways = provide_all(
        WithParents[SQLAlchemyUserGateway], WithParents[SQLAlchemyShopGateway]
    )

    tr_manager = provide(WithParents[SQLAlchemyTransactionManager])


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_session(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(
            config.persistence_uri, decode_responses=True
        ) as redis:
            yield redis
