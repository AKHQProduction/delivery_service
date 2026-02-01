import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
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
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when deleting order %s",
                current_user,
                command.order_id,
            )
            raise AccessDeniedError

        order = await self._order_gateway.load(command.order_id)
        if not order:
            logger.warning("Order not found: order_id=%s", command.order_id)
            return

        if not IsRelatedToShop(order.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to delete "
                "order %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.order_id,
                order.shop_id,
            )
            raise AccessDeniedError

        await self._order_gateway.delete(order)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )
