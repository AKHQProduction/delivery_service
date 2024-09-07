from aiogram.types import TelegramObject
from dishka import (
    Provider,
    Scope,
    AnyOf,
    AsyncContainer,
    make_async_container,
    from_context,
    provide
)

from application.common.access_service import AccessService
from application.employee.gateway import EmployeeReader, EmployeeSaver
from application.shop.gateway import ShopReader, ShopSaver
from application.shop.interactors.change_regular_days_off import (
    ChangeRegularDaysOff
)
from application.shop.interactors.create_shop import CreateShop
from entities.common.token_verifier import TokenVerifier
from application.user.interactors.bot_start import BotStart
from application.user.gateway import UserReader, UserSaver
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.user.interactors.get_user import GetUser
from application.user.interactors.get_users import GetUsers
from entities.shop.services import ShopService
from infrastructure.auth.tg_auth import TgIdentityProvider
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.employee import EmployeeGateway
from infrastructure.gateways.shop import ShopGateway
from infrastructure.gateways.user import UserGateway
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.geopy_processor import GeoProcessor, PyGeoProcessor
from infrastructure.geopy.provider import get_geolocator
from infrastructure.persistence.config import DBConfig
from infrastructure.persistence.provider import (
    get_engine,
    get_async_sessionmaker,
    get_async_session
)
from infrastructure.persistence.commiter import SACommiter
from infrastructure.tg.token_verifier import TgTokenVerifier


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
            UserGateway,
            scope=Scope.REQUEST,
            provides=AnyOf[UserReader, UserSaver]
    )

    provider.provide(
            ShopGateway,
            scope=Scope.REQUEST,
            provides=AnyOf[ShopReader, ShopSaver]
    )

    provider.provide(
            EmployeeGateway,
            scope=Scope.REQUEST,
            provides=AnyOf[EmployeeReader, EmployeeSaver]
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
    provider.provide(ChangeRegularDaysOff, scope=Scope.REQUEST)

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
            PyGeoProcessor,
            scope=Scope.REQUEST,
            provides=GeoProcessor
    )

    provider.provide(
            TgTokenVerifier,
            scope=Scope.REQUEST,
            provides=TokenVerifier
    )

    return provider


def config_provider() -> Provider:
    provider = Provider()

    config = load_all_configs()

    provider.provide(lambda: config.db, scope=Scope.APP, provides=DBConfig)
    provider.provide(lambda: config.geo, scope=Scope.APP, provides=GeoConfig)

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
                user_gateway=user_gateway
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
