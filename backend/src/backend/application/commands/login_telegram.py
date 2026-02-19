import logging
from dataclasses import dataclass

from backend.application.services.user import create_user_via_tg
from backend.infrastructure.persistence.gateways import (
    RedisSessionGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.telegram.widget_auth import (
    TelegramWidgetData,
    WidgetAuth,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoginTelegramCommand:
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int = 0
    hash: str = ""


class LoginTelegramCommandHandler:
    def __init__(
        self,
        widget_auth: WidgetAuth,
        user_gateway: SQLAlchemyUserGateway,
        session_gateway: RedisSessionGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._widget_auth = widget_auth
        self._user_gateway = user_gateway
        self._session_gateway = session_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: LoginTelegramCommand) -> str:
        telegram_id = self._widget_auth.validate(
            TelegramWidgetData(
                id=command.id,
                first_name=command.first_name,
                last_name=command.last_name,
                username=command.username,
                photo_url=command.photo_url,
                auth_date=command.auth_date,
                hash=command.hash,
            )
        )

        user_id = await self._user_gateway.user_id_by_telegram_id(telegram_id)

        if not user_id:
            logger.info(
                "Creating new user via widget login",
                extra={"telegram_id": telegram_id},
            )
            new_user_id = self._user_gateway.next_id()
            user = create_user_via_tg(
                user_id=new_user_id,
                tg_id=telegram_id,
                full_name=command.first_name,
            )
            self._user_gateway.save(user)
            user_id = new_user_id

        session_id = await self._session_gateway.set_session(user_id)
        logger.info(
            "Session created",
            extra={"user_id": str(user_id), "telegram_id": telegram_id},
        )
        await self._tr_manager.commit()

        return session_id
