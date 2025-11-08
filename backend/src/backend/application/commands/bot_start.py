import logging
from dataclasses import dataclass

from backend.application.interfaces import (
    CreateUserViaTgDTO,
    IdentityProvider,
    ShopGateway,
    TransactionManager,
    UserGateway,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotStartCommand:
    tg_id: int
    full_name: str


class BotStartCommandHandler:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_gateway: UserGateway,
        shop_gateway: ShopGateway,
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
            await self._user_gateway.create_user_via_tg(
                CreateUserViaTgDTO(
                    user_id=new_user_id,
                    tg_id=command.tg_id,
                    full_name=command.full_name,
                )
            )
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
