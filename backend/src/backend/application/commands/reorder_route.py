import logging
from dataclasses import dataclass
from datetime import date

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.route_gateway import (
    RouteGeometryReadModel,
)
from backend.application.errors import EntityNotFoundError
from backend.application.policies.access import ensure_can_manage
from backend.application.services.edge_preference_collector import (
    extract_edges,
)
from backend.application.services.route_builder import (
    collect_waypoints,
    resolve_time_slot,
    sort_orders_by_sequence,
)
from backend.application.vars import OrderId, TimeSlotId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRouteEdgeHistoryGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager
from backend.infrastructure.tsp_solvers.osrm import OSRMClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReorderRouteCommand:
    delivery_date: date
    order_id: OrderId
    new_position: int
    time_slot_id: TimeSlotId | None = None


@dataclass(frozen=True)
class ReorderRouteResult:
    geometry: RouteGeometryReadModel


class ReorderRouteCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        route_edge_history_gateway: SQLAlchemyRouteEdgeHistoryGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        osrm_client: OSRMClient,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._edge_gateway = route_edge_history_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._osrm = osrm_client
        self._tr_manager = tr_manager

    async def handle(self, command: ReorderRouteCommand) -> ReorderRouteResult:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        logger.info(
            "Reorder requested: date=%s, order=%s, new_pos=%d, slot=%s",
            command.delivery_date,
            command.order_id,
            command.new_position,
            command.time_slot_id,
        )

        route_plan = ensure_exists(
            await self._route_plan_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=command.delivery_date,
                time_slot_id=command.time_slot_id,
            ),
            "RoutePlan",
        )

        if command.order_id not in route_plan.order_sequence:
            logger.warning(
                "Order %s not in route plan %s sequence",
                command.order_id,
                route_plan.id,
            )
            raise EntityNotFoundError(entity="Order in route sequence")

        old_pos = route_plan.order_sequence.index(command.order_id)
        route_plan.order_sequence.remove(command.order_id)
        pos = max(0, min(command.new_position, len(route_plan.order_sequence)))
        route_plan.order_sequence.insert(pos, command.order_id)

        logger.info(
            "Route plan %s: order %s moved %d -> %d",
            route_plan.id,
            command.order_id,
            old_pos,
            pos,
        )

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
        logger.info("Route plan %s reordered", route_plan.id)

        shop = await self._shop_gateway.load_shop(current_user.shop_id)
        shop_coords = CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
        )

        routable, _ = sort_orders_by_sequence(
            orders, route_plan.order_sequence
        )
        waypoints = (
            collect_waypoints(shop_coords, routable) if shop_coords else []
        )
        raw = (
            await self._osrm.get_route_geometry(waypoints)
            if waypoints
            else None
        )

        geometry = RouteGeometryReadModel(
            encoded_polyline=raw.encoded_polyline if raw else "",
            distance_meters=raw.distance_meters if raw else 0,
            duration_seconds=raw.duration_seconds if raw else 0,
        )

        return ReorderRouteResult(geometry=geometry)
