from backend.application.interfaces import IdentityProvider
from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway


class TelegramIdentityProvider(IdentityProvider):
    def __init__(
        self, telegram_id: int, user_gateway: SQLAlchemyUserGateway
    ) -> None:
        self._telegram_id = telegram_id
        self._user_gateway = user_gateway

    async def current_user_id(self) -> UserId | None:
        return await self._user_gateway.user_id_by_telegram_id(
            self._telegram_id
        )
