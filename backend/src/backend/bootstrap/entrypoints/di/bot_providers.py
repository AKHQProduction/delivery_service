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
    CreateShopCommandHandler,
)
from backend.application.usecases.invite_employee.accept_invite import (
    AcceptInviteCommandHandler,
)
from backend.infrastructure.idp import (
    IdentityProvider,
    TelegramBotIdentityProvider,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)


class BotInteractorsProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        BotStartCommandHandler,
        CreateShopCommandHandler,
        AcceptInviteCommandHandler,
    )


class TelegramProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def current_user(self, middleware_data: AiogramMiddlewareData) -> User:
        return cast("User", middleware_data.get("event_from_user"))

    @provide
    def idp(
        self,
        user: "User",
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> IdentityProvider:
        return TelegramBotIdentityProvider(
            telegram_id=user.id,
            user_gateway=user_gateway,
            shop_gateway=shop_gateway,
        )
