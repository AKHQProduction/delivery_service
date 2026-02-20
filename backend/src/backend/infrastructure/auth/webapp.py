import logging

from fastapi import Request

from backend.application.services.user import create_user_via_tg
from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway
from backend.infrastructure.telegram.auth import (
    Headers,
    WebAppAuth,
    WebAppAuthError,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


class WebAppAuthHandler:
    def __init__(
        self,
        auth: WebAppAuth,
        user_gateway: SQLAlchemyUserGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._auth = auth
        self._user_gateway = user_gateway
        self._tr_manager = tr_manager

    async def authenticate(self, request: Request) -> UserId | None:
        try:
            webapp_user = self._auth.validate(Headers(request.headers))
        except WebAppAuthError:
            return None

        user_id = await self._user_gateway.user_id_by_telegram_id(
            webapp_user.id
        )
        if user_id:
            return user_id

        full_name = webapp_user.first_name
        if webapp_user.last_name:
            full_name += f" {webapp_user.last_name}"

        new_user_id = self._user_gateway.next_id()
        user = create_user_via_tg(
            user_id=new_user_id,
            tg_id=webapp_user.id,
            full_name=full_name,
        )
        self._user_gateway.save(user)
        await self._tr_manager.commit()

        logger.info(
            "Auto-registered new user via WebApp: telegram_id=%s, user_id=%s",
            webapp_user.id,
            new_user_id,
        )
        return new_user_id
