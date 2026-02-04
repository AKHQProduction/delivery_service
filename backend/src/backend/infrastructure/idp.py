from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import AuthorizationError
from backend.application.vars import ShopRole, UserId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)


class TelegramIdentityProvider:
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
