import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.route_builder import remove_order_from_route
from backend.application.vars import OrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteOrderCommand:
    order_id: OrderId


class DeleteOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
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

        route_plan = await self._route_plan_gateway.find_by_order(order.id)
        if route_plan:
            remove_order_from_route(route_plan, order.id)
            logger.info(
                "Removed order %s from route plan %s",
                order.id,
                route_plan.id,
            )

        await self._order_gateway.delete(order)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )
