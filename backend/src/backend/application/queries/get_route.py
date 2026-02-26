import logging
from dataclasses import dataclass
from datetime import date

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.route_gateway import (
    RouteGeometryReadModel,
    RouteReadModel,
)
from backend.application.policies.access import ensure_can_manage
from backend.application.services.edge_preference_collector import (
    PREFERENCE_WINDOW_DAYS,
    build_preference_map,
)
from backend.application.services.route_builder import (
    build_route_read_model,
    collect_waypoints,
    create_route_plan,
    resolve_time_slot,
    sort_orders_by_sequence,
)
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.vars import TimeSlotId
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
class GetRouteQuery:
    delivery_date: date
    time_slot_id: TimeSlotId | None = None


class GetRouteQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        route_edge_history_gateway: SQLAlchemyRouteEdgeHistoryGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        route_optimizer: RouteOptimizer,
        osrm_client: OSRMClient,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._edge_gateway = route_edge_history_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._route_optimizer = route_optimizer
        self._osrm = osrm_client
        self._tr_manager = tr_manager

    async def handle(self, query: GetRouteQuery) -> RouteReadModel:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        time_slot_label, start_time, end_time = await resolve_time_slot(
            self._time_slot_gateway, query.time_slot_id
        )

        orders = await self._order_gateway.load_by_date(
            shop_id=current_user.shop_id,
            delivery_date=query.delivery_date,
            start_time=start_time,
            end_time=end_time,
        )

        route_plan = await self._route_plan_gateway.load_by_date(
            shop_id=current_user.shop_id,
            delivery_date=query.delivery_date,
            time_slot_id=query.time_slot_id,
        )

        shop = await self._shop_gateway.load_shop(current_user.shop_id)
        shop_coords = CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
        )

        if route_plan:
            routable, unroutable = sort_orders_by_sequence(
                orders, route_plan.order_sequence
            )
        else:
            optimized_ids = None
            if shop_coords:
                try:
                    pref_map = (
                        build_preference_map(
                            await self._edge_gateway.load_preferences(
                                current_user.shop_id, PREFERENCE_WINDOW_DAYS
                            )
                        )
                        or None
                    )
                except Exception as exc:
                    logger.exception(
                        "Failed to load edge preferences [%s]",
                        exc.__class__.__name__,
                    )
                    pref_map = None
                optimized_ids = await self._route_optimizer.compute(
                    shop_coords, orders, pref_map
                )

            route_plan = create_route_plan(
                route_plan_gateway=self._route_plan_gateway,
                shop_id=current_user.shop_id,
                delivery_date=query.delivery_date,
                time_slot_id=query.time_slot_id,
                orders=orders,
                optimized_ids=optimized_ids,
            )
            await self._tr_manager.commit()

            routable, unroutable = sort_orders_by_sequence(
                orders, route_plan.order_sequence
            )

        geometry = None
        if shop_coords and routable:
            waypoints = collect_waypoints(shop_coords, routable)
            raw = await self._osrm.get_route_geometry(waypoints)
            if raw:
                geometry = RouteGeometryReadModel(
                    encoded_polyline=raw.encoded_polyline,
                    distance_meters=raw.distance_meters,
                    duration_seconds=raw.duration_seconds,
                )

        return build_route_read_model(
            route_plan_id=route_plan.id,
            delivery_date=query.delivery_date.strftime("%d.%m.%Y"),
            time_slot=time_slot_label,
            ordered_orders=routable,
            unroutable_orders=unroutable,
            geometry=geometry,
        )
