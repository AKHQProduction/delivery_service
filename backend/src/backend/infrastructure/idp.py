from fastapi import Request

from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import AuthorizationError
from backend.application.vars import ShopRole, UserId
from backend.infrastructure.auth.handler import AuthChain
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)


class IdentityProvider:
    def __init__(self, shop_gateway: SQLAlchemyShopGateway) -> None:
        self._shop_gateway = shop_gateway

    async def current_user_id(self) -> UserId | None:
        raise NotImplementedError

    async def current_user(self) -> CurrentUserDTO:
        user_id = await self.current_user_id()
        if user_id and (
            membership := await self._shop_gateway.load_membership(user_id)
        ):
            return CurrentUserDTO(
                user_id=user_id,
                shop_id=membership.shop_id,
                role=ShopRole(membership.role.name),
                full_name=membership.name,
            )
        raise AuthorizationError


class TelegramBotIdentityProvider(IdentityProvider):
    def __init__(
        self,
        telegram_id: int,
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        super().__init__(shop_gateway)
        self._telegram_id = telegram_id
        self._user_gateway = user_gateway

    async def current_user_id(self) -> UserId | None:
        return await self._user_gateway.user_id_by_telegram_id(
            self._telegram_id
        )


class ApiIdentityProvider(IdentityProvider):
    def __init__(
        self,
        auth_chain: AuthChain,
        request: Request,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        super().__init__(shop_gateway)
        self._auth_chain = auth_chain
        self._request = request

    async def current_user_id(self) -> UserId | None:
        return await self._auth_chain.authenticate(self._request)
