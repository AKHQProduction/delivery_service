# ruff: noqa: E501
import logging
from typing import AsyncGenerator, AsyncIterable, AsyncIterator

from aiogram import Bot
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
from dishka.integrations.aiogram import AiogramMiddlewareData
from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from delivery_service.application.commands.add_new_product import (
    AddNewProductHandler,
    AddNewProductRequest,
)
from delivery_service.application.commands.add_new_staff_member import (
    AddNewStaffMemberHandler,
    AddNewStaffMemberRequest,
)
from delivery_service.application.commands.bot_start import (
    BotStartHandler,
    BotStartRequest,
)
from delivery_service.application.commands.create_new_shop import (
    CreateNewShopHandler,
    CreateNewShopRequest,
)
from delivery_service.application.commands.delete_product import (
    DeleteProductHandler,
    DeleteProductRequest,
)
from delivery_service.application.commands.discard_staff_member import (
    DiscardStaffMemberHandler,
    DiscardStaffMemberRequest,
)
from delivery_service.application.commands.edit_product import (
    EditProductHandler,
    EditProductRequest,
)
from delivery_service.application.common.behaviors.commition import (
    CommitionBehavior,
)
from delivery_service.application.common.behaviors.telegram_checker import (
    TelegramCheckerBehavior,
)
from delivery_service.application.common.factories.product_factory import (
    ProductFactory,
)
from delivery_service.application.common.factories.service_user_factory import (
    ServiceUserFactory,
)
from delivery_service.application.common.factories.shop_factory import (
    ShopFactory,
)
from delivery_service.application.common.factories.staff_member_factory import (
    StaffMemberFactory,
)
from delivery_service.application.common.markers.command import (
    TelegramCommand,
)
from delivery_service.bootstrap.configs import (
    DatabaseConfig,
    RabbitConfig,
    RedisConfig,
    TGConfig,
)
from delivery_service.domain.products.access_service import (
    ProductAccessService,
)
from delivery_service.infrastructure.adapters.id_generator import (
    IDGeneratorImpl,
)
from delivery_service.infrastructure.adapters.idp import (
    TelegramIdentityProvider,
)
from delivery_service.infrastructure.adapters.social_network_checker import (
    SocialNetworkCheckerImpl,
)
from delivery_service.infrastructure.integration.geopy.geolocator import (
    Geolocator,
)
from delivery_service.infrastructure.integration.telegram.view_manager import (
    TelegramViewManager,
)
from delivery_service.infrastructure.persistence.adapters.product_repository import (
    SQLAlchemyProductRepository,
)
from delivery_service.infrastructure.persistence.adapters.role_repository import (
    SQLAlchemyRoleRepository,
)
from delivery_service.infrastructure.persistence.adapters.service_user_repository import (
    SQLAlchemyServiceUserRepository,
)
from delivery_service.infrastructure.persistence.adapters.shop_repository import (
    SQLAlchemyShopRepository,
)
from delivery_service.infrastructure.persistence.adapters.social_network_dao import (
    SQlAlchemySocialNetworkGateway,
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
    rabbit_config = from_context(RabbitConfig)


class ApplicationProvider(Provider):
    id_generator = provide(WithParents[IDGeneratorImpl], scope=Scope.APP)


class ApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        BotStartHandler,
        CreateNewShopHandler,
        AddNewStaffMemberHandler,
        DiscardStaffMemberHandler,
        AddNewProductHandler,
        EditProductHandler,
        DeleteProductHandler,
    )
    behaviors = provide_all(CommitionBehavior, TelegramCheckerBehavior)
    fabrics = provide_all(
        StaffMemberFactory, ServiceUserFactory, ShopFactory, ProductFactory
    )


class BazarioProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def registry(self) -> Registry:
        registry = Registry()

        registry.add_request_handler(BotStartRequest, BotStartHandler)
        registry.add_request_handler(
            CreateNewShopRequest, CreateNewShopHandler
        )
        registry.add_request_handler(
            AddNewStaffMemberRequest, AddNewStaffMemberHandler
        )
        registry.add_request_handler(
            DiscardStaffMemberRequest, DiscardStaffMemberHandler
        )
        registry.add_request_handler(
            AddNewProductRequest, AddNewProductHandler
        )
        registry.add_request_handler(EditProductRequest, EditProductHandler)
        registry.add_request_handler(
            DeleteProductRequest, DeleteProductHandler
        )

        registry.add_pipeline_behaviors(Request, CommitionBehavior)
        registry.add_pipeline_behaviors(
            TelegramCommand, TelegramCheckerBehavior
        )
        return registry

    resolver = provide(WithParents[DishkaResolver])
    dispatcher = provide(WithParents[Dispatcher])


class DomainProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SQLAlchemyStaffMemberRepository],
        WithParents[SQLAlchemyRoleRepository],
        WithParents[SQLAlchemyServiceUserRepository],
        WithParents[SQLAlchemyShopRepository],
        WithParents[SQLAlchemyProductRepository],
    )
    services = provide(ProductAccessService, scope=Scope.APP)


class InfrastructureAdaptersProvider(Provider):
    scope = Scope.REQUEST

    transaction = provide(WithParents[SQLAlchemyTransactionManager])
    dao = provide(SQlAlchemySocialNetworkGateway)
    social_network_checker = provide(WithParents[SocialNetworkCheckerImpl])


class TelegramProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    def get_current_telegram_user_id(
        self, middleware_data: AiogramMiddlewareData
    ) -> int | None:
        if current_chat := middleware_data.get("event_chat"):
            return current_chat.id
        return None

    @provide(scope=scope.REQUEST)
    def get_current_bot(
        self, middleware_data: AiogramMiddlewareData
    ) -> Bot | None:
        if bot := middleware_data.get("bot"):
            return bot
        return None

    idp = provide(WithParents[TelegramIdentityProvider])

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


class GeopyProvider(Provider):
    @provide(scope=Scope.APP)
    async def geopy_provider(self) -> AsyncGenerator[Nominatim, None]:
        async with Nominatim(
            user_agent="My GeoPy agent",
            adapter_factory=AioHTTPAdapter,
            timeout=10,  # type: ignore[reportArgumentType]
        ) as geolocator:
            yield geolocator

    geolocator = provide(WithParents[Geolocator], scope=Scope.REQUEST)
