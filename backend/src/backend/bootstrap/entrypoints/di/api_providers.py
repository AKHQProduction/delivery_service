from dishka import Provider, Scope, from_context, provide, provide_all
from fastapi import Request

from backend.application.commands.create_product import (
    CreateProductCommandHandler,
)
from backend.application.commands.edit_product import EditProductCommandHandler
from backend.application.interfaces import IdentityProvider
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.telegram.auth import Headers, InitData, WebAppAuth


class APIInteractorsProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        CreateProductCommandHandler, EditProductCommandHandler
    )


class WebAppProvider(Provider):
    scope = Scope.REQUEST
    request = from_context(provides=Request)

    auth = provide(WebAppAuth)

    @provide
    async def get_headers(self, request: Request) -> Headers:
        return Headers(request.headers)

    @provide
    async def init_data(self, auth: WebAppAuth) -> InitData:
        return auth.with_init_data()

    @provide
    def current_user_id(self, init_data: InitData) -> int:
        return init_data.user.id

    @provide
    def idp(
        self,
        current_user_id: int,
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> IdentityProvider:
        return TelegramIdentityProvider(
            telegram_id=current_user_id,
            user_gateway=user_gateway,
            shop_gateway=shop_gateway,
        )
