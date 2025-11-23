import logging
from dataclasses import dataclass

from backend.application.errors import (
    EntityNotFoundError,
    UserAlreadyRelatedToShopError,
)
from backend.application.interfaces import (
    CreateUserViaTgDTO,
    IdentityProvider,
    ShopGateway,
    TransactionManager,
    UserGateway,
)
from backend.application.interfaces.gateways.shop_gateway import ShopEmployee
from backend.application.usecases.invite_employee.interfaces import LinkGateway

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AcceptInviteCommand:
    payload: str
    tg_id: int
    full_name: str


class AcceptInviteCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        shop_gateway: ShopGateway,
        user_gateway: UserGateway,
        link_gateway: LinkGateway,
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

        link = await self._link_gateway.load_by_payload(command.payload)
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

        current_user_id = await self._idp.current_user_id()
        if not current_user_id:
            logger.info("Creating new user via Telegram")
            new_user_id = self._user_gateway.next_id()
            await self._user_gateway.create_user_via_tg(
                CreateUserViaTgDTO(
                    user_id=new_user_id,
                    tg_id=command.tg_id,
                    full_name=command.full_name,
                )
            )
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

        await self._shop_gateway.add_employee(
            ShopEmployee(
                user_id=user_id,
                shop_id=link.shop_id,
                full_name=link.full_name,
                role=link.role,
            )
        )
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
