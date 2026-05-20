import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.policies.access import ensure_is_owner
from backend.application.services.shop import NewShopAddressDTO, update_shop
from backend.application.vars import ShopRepeatOrderMode
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditShopCommand:
    address: NewShopAddressDTO | None = None
    repeat_order_mode: ShopRepeatOrderMode | None = None


class EditShopCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditShopCommand) -> None:
        logger.info(
            "Editing shop: address=%s repeat_order_mode=%s",
            command.address,
            command.repeat_order_mode,
        )

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        shop = ensure_exists(
            await self._shop_gateway.load_shop(current_user.shop_id),
            "Shop",
        )

        update_shop(
            shop,
            address=command.address,
            repeat_order_mode=command.repeat_order_mode,
        )

        await self._tr_manager.commit()

        logger.info(
            "Successfully edited shop: shop_id=%s", current_user.shop_id
        )
