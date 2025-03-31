# ruff: noqa: E501
import logging
from typing import AsyncIterable, AsyncIterator

from aiogram.types import TelegramObject
from bazario import Request
from bazario.asyncio import Dispatcher, Registry
from bazario.asyncio.resolvers.dishka import DishkaResolver
from dishka import (
    Provider,
    Scope,
    WithParents,
    from_context,
    provide,
    provide_all,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from delivery_service.application.behaviors.commition_behavior import (
    CommitionBehavior,
)
from delivery_service.application.commands.bot_start import (
    BotStartHandler,
    BotStartRequest,
)
from delivery_service.bootstrap.configs import (
    DatabaseConfig,
    RedisConfig,
    TGConfig,
)
from delivery_service.infrastructure.adapters.factories.staff_member_factory import (
    StaffMemberFactoryImpl,
)
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)
from delivery_service.infrastructure.integration.telegram.view_manager import (
    TelegramViewManager,
)
from delivery_service.infrastructure.persistence.adapters.role_repository import (
    SQLAlchemyRoleRepository,
)
from delivery_service.infrastructure.persistence.adapters.staff_member_repository import (
    SQLAlchemyStaffMemberRepository,
)
from delivery_service.infrastructure.persistence.transaction_manager import (
    SQLAlchemyTransactionManager,
)

logger = logging.getLogger(__name__)


class AppConfigProvider(Provider):
    scope = Scope.APP

    tg_config = from_context(TGConfig)
    database_config = from_context(DatabaseConfig)
    redis_config = from_context(RedisConfig)


class ApplicationProvider(Provider):
    id_generator = provide(WithParents[IDGeneratorImpl], scope=Scope.APP)


class ApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(BotStartHandler)
    behaviors = provide_all(CommitionBehavior)


class BazarioProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def registry(self) -> Registry:
        registry = Registry()

        registry.add_request_handler(BotStartRequest, BotStartHandler)
        registry.add_pipeline_behaviors(Request, CommitionBehavior)

        return registry

    resolver = provide(WithParents[DishkaResolver])
    dispatcher = provide(WithParents[Dispatcher])


class DomainProvider(Provider):
    scope = Scope.REQUEST

    fabrics = provide_all(WithParents[StaffMemberFactoryImpl])
    repositories = provide_all(
        WithParents[SQLAlchemyStaffMemberRepository],
        WithParents[SQLAlchemyRoleRepository],
    )


class InfrastructureAdaptersProvider(Provider):
    scope = Scope.REQUEST

    transaction = provide(WithParents[SQLAlchemyTransactionManager])


class TelegramProvider(Provider):
    scope = Scope.REQUEST
    telegram_obj = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    def get_current_telegram_user_id(self, obj: TelegramObject) -> int | None:
        logging.info(obj)

    view_manager = provide(
        WithParents[TelegramViewManager],
    )


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(
        self, config: DatabaseConfig
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(config.uri)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        factory = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        logger.debug("Session provider was initialized")
        return factory

    @provide
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session
