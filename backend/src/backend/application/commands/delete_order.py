import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.order_payment import (
    revert_balance_payment,
)
from backend.application.services.payment_method import (
    is_balance_payment_method,
)
from backend.application.services.route_builder import remove_order_from_route
from backend.application.vars import OrderId, today
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
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
        client_gateway: SQLAlchemyClientGateway,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
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

        order = await self._order_gateway.load_with_items_for_update(
            command.order_id
        )
        if not order:
            return

        ensure_related_to_shop(current_user, order.shop_id)

        if (
            order.is_paid
            and is_balance_payment_method(name=order.payment_method)
            and order.date >= today()
        ):
            client = await self._client_gateway.load_for_update(
                order.client_id
            )
            if client is not None:
                revert_balance_payment(order, client)

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
