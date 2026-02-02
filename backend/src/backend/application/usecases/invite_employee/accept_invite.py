import asyncio
import logging
from dataclasses import dataclass

from backend.application.errors import (
    EntityNotFoundError,
    UserAlreadyRelatedToShopError,
)
from backend.application.services.shop import create_membership
from backend.application.services.user import create_user_via_tg
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    RedisLinkGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AcceptInviteCommand:
    payload: str
    tg_id: int
    full_name: str


class AcceptInviteCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
        user_gateway: SQLAlchemyUserGateway,
        link_gateway: RedisLinkGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway
        self._user_gateway = user_gateway
        self._link_gateway = link_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: AcceptInviteCommand) -> None:
        logger.info(
            "Processing invite acceptance",
            extra={"payload": command.payload, "tg_id": command.tg_id},
        )

        link, current_user_id = await asyncio.gather(
            self._link_gateway.load_by_payload(command.payload),
            self._idp.current_user_id(),
        )

        if not link:
            logger.warning(
                "Invite link not found",
                extra={"payload": command.payload},
            )
            raise EntityNotFoundError(entity="Invite link")

        logger.debug(
            "Invite link found",
            extra={
                "shop_id": link.shop_id,
                "role": link.role,
                "full_name": link.full_name,
            },
        )
        if not current_user_id:
            logger.info("Creating new user via Telegram")
            new_user_id = self._user_gateway.next_id()
            user = create_user_via_tg(
                user_id=new_user_id,
                tg_id=command.tg_id,
                full_name=command.full_name,
            )
            self._user_gateway.save(user)
            logger.info(
                "New user created",
                extra={"user_id": new_user_id, "tg_id": command.tg_id},
            )
            user_id = new_user_id
        elif current_user_id and await self._shop_gateway.relate_to_shop(
            current_user_id
        ):
            logger.warning(
                "User already related to shop",
                extra={"user_id": current_user_id},
            )
            raise UserAlreadyRelatedToShopError
        else:
            logger.debug(
                "Using existing user",
                extra={"user_id": current_user_id},
            )
            user_id = current_user_id

        role_id = await self._shop_gateway.get_role_id(link.role)
        membership = create_membership(
            user_id=user_id,
            shop_id=link.shop_id,
            role_id=role_id,
            name=link.full_name,
        )
        self._shop_gateway.save(membership)

        logger.info(
            "Employee added to shop",
            extra={
                "user_id": user_id,
                "shop_id": link.shop_id,
                "role": link.role,
            },
        )

        await self._link_gateway.delete(command.payload)
        logger.debug("Invite link deleted", extra={"payload": command.payload})

        await self._tr_manager.commit()
        logger.info("Invite acceptance completed successfully")
