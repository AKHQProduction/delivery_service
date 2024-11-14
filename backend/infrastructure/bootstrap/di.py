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

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.file_manager import FileManager
from application.common.geo import GeoProcessor
from application.common.identity_provider import IdentityProvider
from application.common.webhook_manager import TokenVerifier, WebhookManager
from application.employee.commands.add_employee import AddEmployee
from application.employee.commands.edit_employee import (
    ChangeEmployee,
)
from application.employee.commands.remove_employee import RemoveEmployee
from application.employee.gateway import (
    EmployeeGateway,
    EmployeeReader,
)
from application.employee.queries.get_employee_card import GetEmployeeCard
from application.employee.queries.get_employees_cards import (
    GetEmployeeCards,
)
from application.goods.gateway import GoodsReader, GoodsSaver
from application.goods.interactors.add_goods import AddGoods
from application.goods.interactors.delete_goods import DeleteGoods
from application.goods.interactors.edit_goods import EditGoods
from application.goods.interactors.get_goods import GetGoods
from application.goods.interactors.get_many_goods import GetManyGoods
from application.goods.interactors.get_many_goods_by_admin import (
    GetManyGoodsByAdmin,
)
from application.order.gateway import (
    OrderItemReader,
    OrderItemSaver,
    OrderReader,
    OrderSaver,
)
from application.order.interactors.create_order import CreateOrder
from application.order.interactors.delete_order import DeleteOrder
from application.order.interactors.delete_order_item import DeleteOrderItem
from application.order.interactors.edit_order_item_quantity import (
    EditOrderItemQuantity,
)
from application.order.interactors.get_order import GetOrder
from application.profile.commands.update_address_by_yourself import (
    ChangeAddress,
)
from application.profile.commands.update_phone_number_by_yourself import (
    UpdatePhoneNumberByYourself,
)
from application.shop.gateway import ShopGateway, ShopReader, ShopSaver
from application.shop.interactors.change_regular_days_off import (
    ChangeRegularDaysOff,
)
from application.shop.interactors.change_special_days_off import (
    ChangeSpecialDaysOff,
)
from application.shop.interactors.create_shop import CreateShop
from application.shop.interactors.delete_shop import DeleteShop
from application.shop.interactors.resume_shop import ResumeShop
from application.shop.interactors.setup_all_shops import SetupAllShop
from application.shop.interactors.stop_shop import StopShop
from application.shop.queries.get_shop_info import GetShopInfo
from application.user.gateway import UserReader, UserSaver
from application.user.interactors.admin_bot_start import AdminBotStart
from application.user.interactors.get_user import GetUser
from application.user.interactors.get_users import GetUsers
from application.user.interactors.shop_bot_start import ShopBotStart
from infrastructure.auth.tg_auth import TgIdentityProvider
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.employee import (
    EmployeeMapper,
    SqlalchemyEmployeeReader,
)
from infrastructure.gateways.goods import GoodsGateway
from infrastructure.gateways.order import OrderGateway, OrderItemGateway
from infrastructure.gateways.shop import ShopMapper, SqlalchemyShopReader
from infrastructure.gateways.user import UserGateway
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.geopy_processor import PyGeoProcessor
from infrastructure.geopy.provider import get_geolocator
from infrastructure.persistence.commiter import SACommiter
from infrastructure.persistence.config import DBConfig
from infrastructure.persistence.provider import (
    get_async_session,
    get_async_sessionmaker,
    get_engine,
)
from infrastructure.s3.config import S3Config
from infrastructure.s3.file_manager import S3FileManager
from infrastructure.tg.bot_webhook_manager import BotWebhookManager
from infrastructure.tg.config import ProjectConfig, WebhookConfig


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        UserGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[UserReader, UserSaver],
    )

    provider.provide(
        ShopMapper,
        scope=Scope.REQUEST,
        provides=AnyOf[ShopGateway, ShopSaver],
    )

    provider.provide(
        SqlalchemyShopReader, scope=Scope.REQUEST, provides=ShopReader
    )

    provider.provide(
        EmployeeMapper,
        scope=Scope.REQUEST,
        provides=EmployeeGateway,
    )

    provider.provide(
        SqlalchemyEmployeeReader, scope=Scope.REQUEST, provides=EmployeeReader
    )

    provider.provide(
        GoodsGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[GoodsSaver, GoodsReader],
    )

    provider.provide(
        OrderGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[OrderSaver, OrderReader],
    )

    provider.provide(
        OrderItemGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[OrderItemSaver, OrderItemReader],
    )

    provider.provide(
        SACommiter,
        scope=Scope.REQUEST,
        provides=Commiter,
    )

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
    provider.provide(AdminBotStart, scope=Scope.REQUEST)
    provider.provide(ChangeAddress, scope=Scope.REQUEST)

    provider.provide(GetUser, scope=Scope.REQUEST)
    provider.provide(GetUsers, scope=Scope.REQUEST)

    provider.provide(CreateShop, scope=Scope.REQUEST)
    provider.provide(StopShop, scope=Scope.REQUEST)
    provider.provide(ResumeShop, scope=Scope.REQUEST)
    provider.provide(DeleteShop, scope=Scope.REQUEST)
    provider.provide(ChangeRegularDaysOff, scope=Scope.REQUEST)
    provider.provide(ChangeSpecialDaysOff, scope=Scope.REQUEST)
    provider.provide(SetupAllShop, scope=Scope.REQUEST)
    provider.provide(GetShopInfo, scope=Scope.REQUEST)

    provider.provide(AddGoods, scope=Scope.REQUEST)
    provider.provide(DeleteGoods, scope=Scope.REQUEST)
    provider.provide(EditGoods, scope=Scope.REQUEST)
    provider.provide(GetGoods, scope=Scope.REQUEST)
    provider.provide(GetManyGoods, scope=Scope.REQUEST)
    provider.provide(GetManyGoodsByAdmin, scope=Scope.REQUEST)

    provider.provide(GetEmployeeCards, scope=Scope.REQUEST)
    provider.provide(GetEmployeeCard, scope=Scope.REQUEST)
    provider.provide(AddEmployee, scope=Scope.REQUEST)
    provider.provide(RemoveEmployee, scope=Scope.REQUEST)
    provider.provide(ChangeEmployee, scope=Scope.REQUEST)

    provider.provide(CreateOrder, scope=Scope.REQUEST)
    provider.provide(GetOrder, scope=Scope.REQUEST)
    provider.provide(EditOrderItemQuantity, scope=Scope.REQUEST)
    provider.provide(DeleteOrderItem, scope=Scope.REQUEST)
    provider.provide(DeleteOrder, scope=Scope.REQUEST)

    provider.provide(UpdatePhoneNumberByYourself, scope=Scope.REQUEST)

    return provider


def service_provider() -> Provider:
    provider = Provider()

    provider.provide(AccessService, scope=Scope.REQUEST)

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
        user_id: int,
        user_gateway: UserReader,
        employee_gateway: EmployeeGateway,
    ) -> IdentityProvider:
        identity_provider = TgIdentityProvider(
            user_id=user_id,
            user_gateway=user_gateway,
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
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
