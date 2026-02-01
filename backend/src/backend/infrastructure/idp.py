from backend.application.errors import AuthorizationError
from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.vars import UserId
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
            shop_employee := await self._shop_gateway.get_shop_employee(
                user_id
            )
        ):
            return CurrentUserDTO(
                user_id=user_id,
                shop_id=shop_employee.shop_id,
                role=shop_employee.role,
                full_name=shop_employee.full_name,
            )

        raise AuthorizationError
