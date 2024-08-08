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
from infrastructure.gateways.user import InMemoryUserGateway


def gateway_provider() -> Provider:
    provider = Provider()

    provider.provide(
        InMemoryUserGateway,
        scope=Scope.APP,
        provides=AnyOf[UserReader, UserSaver]
    )

    return provider


def interactor_provider() -> Provider:
    provider = Provider()

    provider.provide(BotStart, scope=Scope.REQUEST)

    return provider


class TgProvider(Provider):
    tg_object = from_context(provides=TelegramObject, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_user(self, obj: TelegramObject) -> User:
        return obj.from_user


def setup_providers() -> list[Provider]:
    providers = [
        gateway_provider(),
        interactor_provider()
    ]

    return providers


def setup_di() -> AsyncContainer:
    providers = setup_providers()
    providers += [TgProvider()]

    container = make_async_container(*providers)

    return container
