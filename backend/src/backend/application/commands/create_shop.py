import logging
from dataclasses import dataclass

from backend.application.errors import (
    AuthorizationError,
    UserAlreadyRelatedToShopError,
)
from backend.application.vars import ShopRole
from backend.domain.services.shop import create_shop
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateNewShopCommand:
    name: str
    owner_full_name: str


class CreateNewShopCommandHandler:
    def __init__(
        self,
        shop_gateway: SQLAlchemyShopGateway,
        identity_provider: TelegramIdentityProvider,
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
            raise AuthorizationError

        if await self._shop_gateway.relate_to_shop(user_id):
            raise UserAlreadyRelatedToShopError

        shop_id = self._shop_gateway.next_id()
        owner_role_id = await self._shop_gateway.get_role_id(ShopRole.OWNER)

        shop = create_shop(
            shop_id=shop_id,
            name=command.name,
            owner_user_id=user_id,
            owner_name=command.owner_full_name,
            owner_role_id=owner_role_id,
        )
        self._shop_gateway.save(shop)

        await self._tr_manager.commit()
        logger.info(
            "Shop created successfully",
            extra={"shop_id": str(shop_id), "shop_name": command.name},
        )
