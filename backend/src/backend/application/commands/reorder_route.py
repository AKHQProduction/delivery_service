import logging
from dataclasses import dataclass
from datetime import date

from backend.application.common import ensure_exists
from backend.application.policies.access import ensure_can_manage
from backend.application.services.edge_preference_collector import (
    extract_edges,
)
from backend.application.services.route_builder import resolve_time_slot
from backend.application.vars import OrderId, TimeSlotId
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
class ReorderRouteCommand:
    delivery_date: date
    order_id: OrderId
    new_position: int
    time_slot_id: TimeSlotId | None = None


class ReorderRouteCommandHandler:
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

    async def handle(self, command: ReorderRouteCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        route_plan = ensure_exists(
            await self._route_plan_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=command.delivery_date,
                time_slot_id=command.time_slot_id,
            ),
            "RoutePlan",
        )

        sequence = list(route_plan.order_sequence)

        if command.order_id not in sequence:
            logger.warning(
                "Order %s not in route plan %s sequence",
                command.order_id,
                route_plan.id,
            )
            return

        sequence.remove(command.order_id)
        pos = max(0, min(command.new_position, len(sequence)))
        sequence.insert(pos, command.order_id)

        route_plan.order_sequence = sequence

        try:
            _, start_time, end_time = await resolve_time_slot(
                self._time_slot_gateway, command.time_slot_id
            )
            orders = await self._order_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=command.delivery_date,
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
