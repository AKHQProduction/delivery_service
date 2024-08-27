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

from application.bot_start import BotStart
from application.change_user_role import ChangeUserRole
from application.common.gateways.user import UserReader, UserSaver
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.get_user import GetUser
from application.get_users import GetUsers
from infrastructure.auth.tg_auth import TgIdentityProvider
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.user import PostgreUserGateway
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


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
            PostgreUserGateway,
            scope=Scope.REQUEST,
            provides=AnyOf[UserReader, UserSaver]
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
    provider.provide(ChangeUserRole, scope=Scope.REQUEST)
    provider.provide(GetUser, scope=Scope.REQUEST)
    provider.provide(GetUsers, scope=Scope.REQUEST)

    return provider


def infrastructure_provider() -> Provider:
    provider = Provider()

    provider.provide(
            PyGeoProcessor,
            scope=Scope.REQUEST,
            provides=GeoProcessor
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
                user_gateway=user_gateway,
        )

        return identity_provider


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider(),
        db_provider(),
        geo_provider(),
        infrastructure_provider(),
        config_provider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
