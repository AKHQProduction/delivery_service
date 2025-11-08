import logging
from dataclasses import dataclass

from backend.application.errors import (
    AuthorizationError,
    UserAlreadyRelatedToShopError,
)
from backend.application.interfaces import ShopGateway, TransactionManager
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
)
from backend.application.interfaces.idp import IdentityProvider

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateNewShopCommand:
    name: str


class CreateNewShopCommandHandler:
    def __init__(
        self,
        shop_gateway: ShopGateway,
        identity_provider: IdentityProvider,
        tr_manager: TransactionManager,
    ) -> None:
        self._shop_gateway = shop_gateway
        self._identity_provider = identity_provider
        self._tr_manager = tr_manager

    async def handle(self, command: CreateNewShopCommand) -> None:
        logger.info(
            "Processing create shop command", extra={"shop_name": command.name}
        )
        user_id = await self._identity_provider.current_user_id()

        if not user_id:
            logger.warning("Unauthorized attempt to create shop")
            raise AuthorizationError

        logger.debug(
            "Checking if user already has a shop",
            extra={"user_id": str(user_id)},
        )
        if await self._shop_gateway.relate_to_shop(user_id):
            logger.warning(
                "User already related to a shop",
                extra={"user_id": str(user_id)},
            )
            raise UserAlreadyRelatedToShopError

        shop_id = self._shop_gateway.next_id()
        logger.info(
            "Creating new shop",
            extra={
                "shop_id": str(shop_id),
                "shop_name": command.name,
                "user_id": str(user_id),
            },
        )
        await self._shop_gateway.create_shop(
            CreateNewShopDTO(
                shop_id=shop_id, name=command.name, user_id=user_id
            )
        )

        await self._tr_manager.commit()
        logger.info(
            "Shop created successfully",
            extra={"shop_id": str(shop_id), "shop_name": command.name},
        )
