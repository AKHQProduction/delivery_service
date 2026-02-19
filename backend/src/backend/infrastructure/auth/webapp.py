from fastapi import Request

from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway
from backend.infrastructure.telegram.auth import (
    Headers,
    WebAppAuth,
    WebAppAuthError,
)


class WebAppAuthHandler:
    def __init__(
        self,
        auth: WebAppAuth,
        user_gateway: SQLAlchemyUserGateway,
    ) -> None:
        self._auth = auth
        self._user_gateway = user_gateway

    async def authenticate(self, request: Request) -> UserId | None:
        try:
            telegram_id = self._auth.validate(Headers(request.headers))
        except WebAppAuthError:
            return None
        return await self._user_gateway.user_id_by_telegram_id(telegram_id)
