from typing import cast

from aiogram.types import User
from dishka import (
    Provider,
    Scope,
    provide,
    provide_all,
)
from dishka.integrations.aiogram import AiogramMiddlewareData

from backend.application.commands import (
    BotStartCommandHandler,
    CreateNewShopCommandHandler,
)
from backend.application.interfaces import IdentityProvider
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyUserGateway,
)


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
