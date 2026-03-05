import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.policies.access import ensure_can_manage
from backend.application.services.edge_preference_collector import (
    extract_edges,
)
from backend.application.services.route_builder import (
    resolve_time_slot,
)
from backend.application.vars import RoutePlanId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRouteEdgeHistoryGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReverseRouteCommand:
    route_plan_id: RoutePlanId


class ReverseRouteCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        route_edge_history_gateway: SQLAlchemyRouteEdgeHistoryGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._edge_gateway = route_edge_history_gateway
        self._time_slot_gateway = time_slot_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: ReverseRouteCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        logger.info(
            "Reverse requested: route_plan=%s",
            command.route_plan_id,
        )

        route_plan = ensure_exists(
            await self._route_plan_gateway.load(command.route_plan_id),
            "RoutePlan",
        )

        route_plan.order_sequence = route_plan.order_sequence[::-1]

        logger.info(
            "Route plan %s: sequence reversed",
            route_plan.id,
        )

        try:
            _, start_time, end_time = await resolve_time_slot(
                self._time_slot_gateway, route_plan.time_slot_id
            )
            orders = await self._order_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=route_plan.delivery_date,
                start_time=start_time,
                end_time=end_time,
            )
            edges = extract_edges(orders, route_plan.order_sequence)
            await self._edge_gateway.upsert_edges(current_user.shop_id, edges)
        except Exception as exc:
            logger.exception(
                "Failed to record edge history for route plan %s [%s]",
                route_plan.id,
                exc.__class__.__name__,
            )

        await self._tr_manager.commit()
        logger.info("Route plan %s reversed", route_plan.id)
