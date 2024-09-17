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
from application.common.identity_provider import IdentityProvider
from application.common.webhook_manager import WebhookManager
from application.employee.gateway import EmployeeReader, EmployeeSaver
from application.employee.interactors.add_employee import AddEmployee
from application.employee.interactors.remove_employee import RemoveEmployee
from application.goods.gateway import GoodsSaver
from application.goods.interactors.add_goods import AddGoods
from application.shop.gateway import ShopReader, ShopSaver
from application.shop.interactors.change_regular_days_off import (
    ChangeRegularDaysOff,
)
from application.shop.interactors.change_special_days_off import (
    ChangeSpecialDaysOff,
)
from application.shop.interactors.create_shop import CreateShop
from application.shop.interactors.delete_shop import DeleteShop
from application.shop.interactors.resume_shop import ResumeShop
from application.shop.interactors.stop_shop import StopShop
from application.user.gateway import UserReader, UserSaver
from application.user.interactors.bot_start import BotStart
from application.user.interactors.get_user import GetUser
from application.user.interactors.get_users import GetUsers
from entities.common.token_verifier import TokenVerifier
from entities.shop.services import ShopService
from infrastructure.auth.tg_auth import TgIdentityProvider
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.employee import EmployeeGateway
from infrastructure.gateways.goods import GoodsGateway
from infrastructure.gateways.shop import ShopGateway
from infrastructure.gateways.user import UserGateway
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.geopy_processor import GeoProcessor, PyGeoProcessor
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
from infrastructure.tg.config import WebhookConfig
from infrastructure.tg.token_verifier import TgTokenVerifier


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        UserGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[UserReader, UserSaver],
    )

    provider.provide(
        ShopGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[ShopReader, ShopSaver],
    )

    provider.provide(
        EmployeeGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[EmployeeReader, EmployeeSaver],
    )

    provider.provide(
        GoodsGateway, scope=Scope.REQUEST, provides=AnyOf[GoodsSaver]
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

    provider.provide(BotStart, scope=Scope.REQUEST)
    provider.provide(GetUser, scope=Scope.REQUEST)
    provider.provide(GetUsers, scope=Scope.REQUEST)

    provider.provide(CreateShop, scope=Scope.REQUEST)
    provider.provide(StopShop, scope=Scope.REQUEST)
    provider.provide(ResumeShop, scope=Scope.REQUEST)
    provider.provide(DeleteShop, scope=Scope.REQUEST)
    provider.provide(ChangeRegularDaysOff, scope=Scope.REQUEST)
    provider.provide(ChangeSpecialDaysOff, scope=Scope.REQUEST)

    provider.provide(AddGoods, scope=Scope.REQUEST)

    provider.provide(AddEmployee, scope=Scope.REQUEST)
    provider.provide(RemoveEmployee, scope=Scope.REQUEST)

    return provider


def service_provider() -> Provider:
    provider = Provider()

    provider.provide(ShopService, scope=Scope.REQUEST)

    return provider


def access_provider() -> Provider:
    provider = Provider()

    provider.provide(AccessService, scope=Scope.REQUEST)

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(
        PyGeoProcessor, scope=Scope.REQUEST, provides=GeoProcessor
    )

    provider.provide(
        TgTokenVerifier, scope=Scope.REQUEST, provides=TokenVerifier
    )

    provider.provide(
        BotWebhookManager, scope=Scope.REQUEST, provides=WebhookManager
    )

    provider.provide(S3FileManager, scope=Scope.REQUEST, provides=FileManager)

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
    ) -> IdentityProvider:
        identity_provider = TgIdentityProvider(
            user_id=user_id,
            user_gateway=user_gateway,
        )

        return identity_provider


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider(),
        db_provider(),
        geo_provider(),
        service_provider(),
        access_provider(),
        infrastructure_provider(),
        config_provider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
