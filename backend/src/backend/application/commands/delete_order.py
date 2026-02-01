import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import OrderId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyOrderGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteOrderCommand:
    order_id: OrderId


class DeleteOrderCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteOrderCommand) -> None:
        logger.info(
            "Deleting order: order_id=%s",
            command.order_id,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = await self._order_gateway.load(command.order_id)
        if not order:
            return

        ensure_related_to_shop(current_user, order.shop_id)

        await self._order_gateway.delete(order)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )
