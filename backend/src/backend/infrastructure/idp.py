from backend.application.errors import AuthorizationError
from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)


class TelegramIdentityProvider(IdentityProvider):
    def __init__(
        self,
        telegram_id: int,
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        self._telegram_id = telegram_id
        self._user_gateway = user_gateway
        self._shop_gateway = shop_gateway

    async def current_user_id(self) -> UserId | None:
        return await self._user_gateway.user_id_by_telegram_id(
            self._telegram_id
        )

    async def current_user(self) -> CurrentUserDTO:
        user_id = await self.current_user_id()
        if user_id:
            role = await self._shop_gateway.role_by_user_id(user_id)
            if role:
                return CurrentUserDTO(user_id=user_id, role=role)
        raise AuthorizationError
