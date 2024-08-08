from aiogram.types import TelegramObject, User
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
from application.common.gateways.user import UserReader, UserSaver
from application.common.uow import UoW
from infrastructure.bootstrap.configs import load_all_configs
from infrastructure.gateways.user import PostgreUserGateway
from infrastructure.persistence.config import DBConfig
from infrastructure.persistence.provider import (
    get_engine,
    get_async_sessionmaker,
    get_async_session
)
from infrastructure.persistence.uow import SAUnitOfWork


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        PostgreUserGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[UserReader, UserSaver]
    )

    provider.provide(
        SAUnitOfWork,
        scope=Scope.REQUEST,
        provides=UoW,
    )

    return provider


def db_provider() -> Provider:
    provider = Provider()

    provider.provide(get_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, scope=Scope.REQUEST)

    return provider


def interactor_provider() -> Provider:
    provider = Provider()

    provider.provide(BotStart, scope=Scope.REQUEST)

    return provider


def config_provider() -> Provider:
    provider = Provider()

    config = load_all_configs()

    provider.provide(lambda: config.db, scope=Scope.APP, provides=DBConfig)

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user(self, obj: TelegramObject) -> User:
        return obj.from_user


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider(),
        db_provider(),
        config_provider(),
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
