import logging

from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import ensure_related_to_shop
from backend.application.services.order_payment import revert_balance_payment
from backend.application.services.payment_method import (
    is_balance_payment_method,
)
from backend.application.services.route_builder import remove_order_from_route
from backend.application.vars import (
    OrderId,
    today,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
)

logger = logging.getLogger(__name__)


class OrderDeletion:
    def __init__(
        self,
        client_gateway: SQLAlchemyClientGateway,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
    ) -> None:
        self._client_gateway = client_gateway
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway

    async def delete(
        self,
        order_id: OrderId,
        current_user: CurrentUserDTO,
    ) -> None:
        order = await self._order_gateway.load_with_items_for_update(order_id)
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
