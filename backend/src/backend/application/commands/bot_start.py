import logging
from dataclasses import dataclass

from backend.application.services.user import create_user_via_tg
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotStartCommand:
    tg_id: int
    full_name: str


class BotStartCommandHandler:
    def __init__(
        self,
        identity_provider: TelegramIdentityProvider,
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = identity_provider
        self._user_gateway = user_gateway
        self._shop_gateway = shop_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: BotStartCommand) -> bool:
        logger.info(
            "Processing bot start command", extra={"tg_id": command.tg_id}
        )
        user_id = await self._idp.current_user_id()

        if not user_id:
            logger.info(
                "Creating new user",
                extra={"tg_id": command.tg_id, "full_name": command.full_name},
            )
            new_user_id = self._user_gateway.next_id()
            user = create_user_via_tg(
                user_id=new_user_id,
                tg_id=command.tg_id,
                full_name=command.full_name,
            )
            self._user_gateway.save(user)
            await self._tr_manager.commit()
            logger.info(
                "User created successfully",
                extra={"user_id": str(new_user_id), "tg_id": command.tg_id},
            )
            return False

        logger.debug(
            "Checking shop relation for existing user",
            extra={"user_id": str(user_id)},
        )
        has_shop = await self._shop_gateway.relate_to_shop(user_id)
        logger.info(
            "User shop relation check completed",
            extra={"user_id": str(user_id), "has_shop": has_shop},
        )
        return has_shop
