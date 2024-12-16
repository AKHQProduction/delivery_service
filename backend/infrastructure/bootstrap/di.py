from aiogram.types import TelegramObject
from dishka import (
    AnyOf,
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)

from application.commands.bot.admin_bot_start import (
    AdminBotStartCommandHandler,
)
from application.commands.bot.shop_bot_start import ShopBotStart
from application.commands.employee.add_employee import (
    AddEmployeeCommandHandler,
)
from application.commands.employee.edit_employee import (
    ChangeEmployeeCommandHandler,
)
from application.commands.employee.remove_employee import (
    RemoveEmployeeCommandHandler,
)
from application.commands.goods.add_goods import AddGoodsCommandHandler
from application.commands.goods.delete_goods import DeleteGoodsCommandHandler
from application.commands.goods.edit_goods import EditGoodsCommandHandler
from application.commands.order.create_order import (
    CreateOrderCommandHandler,
)
from application.commands.order.delete_order import DeleteOrder
from application.commands.order.edit_order_item_quantity import (
    EditOrderItemQuantityCommandHandler,
)
from application.commands.order.remove_order_item import (
    DeleteOrderItemCommandHandler,
)
from application.commands.shop.change_regular_days_off import (
    ChangeRegularDaysOffCommandHandler,
)
from application.commands.shop.change_special_days_off import (
    ChangeSpecialDaysOffCommandHandler,
)
from application.commands.shop.create_shop import CreateShopCommandHandler
from application.commands.shop.delete_shop import DeleteShopCommandHandler
from application.commands.shop.resume_shop import ResumeShopCommandHandler
from application.commands.shop.setup_all_shops import SetupAllShopCommand
from application.commands.shop.stop_shop import StopShopCommandHandler
from application.common.access_service import AccessService
from application.common.file_manager import FileManager
from application.common.geo import GeoProcessor
from application.common.identity_provider import IdentityProvider
from application.common.persistence.employee import (
    EmployeeGateway,
    EmployeeReader,
)
from application.common.persistence.goods import GoodsGateway, GoodsReader
from application.common.persistence.order import OrderGateway, OrderReader
from application.common.persistence.shop import ShopGateway, ShopReader
from application.common.persistence.user import UserGateway, UserReader
from application.common.transaction_manager import TransactionManager
from application.common.webhook_manager import TokenVerifier, WebhookManager
from application.queries.employee.get_employees import GetEmployeeQueryHandler
from application.queries.goods.get_many_goods import (
    GetManyGoodsQueryHandler,
)
from application.queries.goods.get_many_goods_by_admin import (
    GetManyGoodsByAdminQueryHandler,
)
from application.queries.order.get_order import GetOrderQueryHandler
from entities.common.tracker import Tracker
from entities.employee.services import EmployeeService
from entities.goods.service import GoodsService
from entities.order.service import OrderService
from entities.shop.services import ShopService
from entities.user.services import UserService
from infrastructure.auth.tg_auth import TgIdentityProvider
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.employee import (
    SQLAlchemyEmployeeMapper,
    SQLAlchemyEmployeeReader,
)
from infrastructure.gateways.goods import (
    SQLAlchemyGoodsMapper,
    SQLAlchemyGoodsReader,
)
from infrastructure.gateways.order import (
    SQLAlchemyOrderMapper,
    SQLAlchemyOrderReader,
)
from infrastructure.gateways.shop import (
    SQLAlchemyShopMapper,
    SQLAlchemyShopReader,
)
from infrastructure.gateways.user import (
    SQLAlchemyUserMapper,
    SQLAlchemyUserReader,
)
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.geopy_processor import PyGeoProcessor
from infrastructure.geopy.provider import get_geolocator
from infrastructure.persistence.config import DBConfig
from infrastructure.persistence.provider import (
    get_async_session,
    get_async_sessionmaker,
    get_engine,
)
from infrastructure.persistence.tracker import SATracker
from infrastructure.persistence.transaction_manager import SATransactionManager
from infrastructure.s3.config import S3Config
from infrastructure.s3.file_manager import S3FileManager
from infrastructure.tg.bot_webhook_manager import BotWebhookManager
from infrastructure.tg.config import ProjectConfig, WebhookConfig


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        SQLAlchemyUserMapper, scope=Scope.REQUEST, provides=UserGateway
    )
    provider.provide(
        SQLAlchemyUserReader, scope=Scope.REQUEST, provides=UserReader
    )

    provider.provide(
        SQLAlchemyShopMapper, scope=Scope.REQUEST, provides=ShopGateway
    )
    provider.provide(
        SQLAlchemyShopReader, scope=Scope.REQUEST, provides=ShopReader
    )

    provider.provide(
        SQLAlchemyEmployeeMapper,
        scope=Scope.REQUEST,
        provides=EmployeeGateway,
    )

    provider.provide(
        SQLAlchemyEmployeeReader, scope=Scope.REQUEST, provides=EmployeeReader
    )

    provider.provide(
        SQLAlchemyGoodsMapper,
        scope=Scope.REQUEST,
        provides=GoodsGateway,
    )
    provider.provide(
        SQLAlchemyGoodsReader, scope=Scope.REQUEST, provides=GoodsReader
    )

    provider.provide(
        SQLAlchemyOrderMapper,
        scope=Scope.REQUEST,
        provides=OrderGateway,
    )
    provider.provide(
        SQLAlchemyOrderReader, scope=Scope.REQUEST, provides=OrderReader
    )

    provider.provide(
        SATransactionManager,
        scope=Scope.REQUEST,
        provides=TransactionManager,
    )
    provider.provide(SATracker, scope=Scope.REQUEST, provides=Tracker)

    return provider


def db_provider() -> Provider:
    provider = Provider()

    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, scope=Scope.REQUEST)

    return provider


def geo_provider() -> Provider:
    provider = Provider()

    provider.provide(get_geolocator, scope=Scope.REQUEST)

    return provider


def interactor_provider() -> Provider:
    provider = Provider()

    provider.provide(ShopBotStart, scope=Scope.REQUEST)
    provider.provide(AdminBotStartCommandHandler, scope=Scope.REQUEST)

    provider.provide(CreateShopCommandHandler, scope=Scope.REQUEST)
    provider.provide(StopShopCommandHandler, scope=Scope.REQUEST)
    provider.provide(ResumeShopCommandHandler, scope=Scope.REQUEST)
    provider.provide(DeleteShopCommandHandler, scope=Scope.REQUEST)
    provider.provide(ChangeRegularDaysOffCommandHandler, scope=Scope.REQUEST)
    provider.provide(ChangeSpecialDaysOffCommandHandler, scope=Scope.REQUEST)
    provider.provide(SetupAllShopCommand, scope=Scope.REQUEST)

    provider.provide(AddGoodsCommandHandler, scope=Scope.REQUEST)
    provider.provide(DeleteGoodsCommandHandler, scope=Scope.REQUEST)
    provider.provide(EditGoodsCommandHandler, scope=Scope.REQUEST)
    provider.provide(GetManyGoodsQueryHandler, scope=Scope.REQUEST)
    provider.provide(GetManyGoodsByAdminQueryHandler, scope=Scope.REQUEST)

    provider.provide(AddEmployeeCommandHandler, scope=Scope.REQUEST)
    provider.provide(RemoveEmployeeCommandHandler, scope=Scope.REQUEST)
    provider.provide(ChangeEmployeeCommandHandler, scope=Scope.REQUEST)
    provider.provide(GetEmployeeQueryHandler, scope=Scope.REQUEST)

    provider.provide(CreateOrderCommandHandler, scope=Scope.REQUEST)
    provider.provide(GetOrderQueryHandler, scope=Scope.REQUEST)
    provider.provide(EditOrderItemQuantityCommandHandler, scope=Scope.REQUEST)
    provider.provide(DeleteOrderItemCommandHandler, scope=Scope.REQUEST)
    provider.provide(DeleteOrder, scope=Scope.REQUEST)

    return provider


class QueriesProvider(Provider):
    scope = Scope.REQUEST


def service_provider() -> Provider:
    provider = Provider()

    provider.provide_all(
        AccessService,
        UserService,
        ShopService,
        EmployeeService,
        GoodsService,
        OrderService,
        scope=Scope.REQUEST,
    )

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(
        PyGeoProcessor, scope=Scope.REQUEST, provides=GeoProcessor
    )

    provider.provide(
        BotWebhookManager,
        scope=Scope.REQUEST,
        provides=AnyOf[WebhookManager, TokenVerifier],
    )

    provider.provide(S3FileManager, scope=Scope.APP, provides=FileManager)

    return provider


def config_provider() -> Provider:
    provider = Provider()

    config = load_all_configs()

    provider.provide(lambda: config.db, scope=Scope.APP, provides=DBConfig)
    provider.provide(lambda: config.geo, scope=Scope.APP, provides=GeoConfig)
    provider.provide(
        lambda: config.webhook, scope=Scope.APP, provides=WebhookConfig
    )
    provider.provide(lambda: config.s3, scope=Scope.APP, provides=S3Config)
    provider.provide(
        lambda: config.settings, scope=Scope.APP, provides=ProjectConfig
    )

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, obj: TelegramObject) -> int:
        return obj.from_user.id

    @provide(scope=Scope.REQUEST)
    async def get_identity_provider(
        self,
        tg_id: int,
        user_mapper: UserGateway,
        employee_gateway: EmployeeGateway,
    ) -> IdentityProvider:
        identity_provider = TgIdentityProvider(
            tg_id=tg_id,
            user_mapper=user_mapper,
            employee_gateway=employee_gateway,
        )

        return identity_provider


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider(),
        db_provider(),
        geo_provider(),
        service_provider(),
        infrastructure_provider(),
        config_provider(),
        QueriesProvider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
