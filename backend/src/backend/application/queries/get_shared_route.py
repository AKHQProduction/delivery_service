import logging

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.route_gateway import (
    RouteGeometryReadModel,
    RouteReadModel,
)
from backend.application.services.route_builder import (
    build_route_read_model,
    collect_waypoints,
    resolve_time_slot,
    sort_orders_by_sequence,
)
from backend.application.vars import RoutePlanId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.tsp_solvers.osrm import OSRMClient

logger = logging.getLogger(__name__)


class GetSharedRouteQueryHandler:
    def __init__(
        self,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        osrm_client: OSRMClient,
    ) -> None:
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._osrm = osrm_client

    async def handle(self, route_plan_id: RoutePlanId) -> RouteReadModel:
        route_plan = ensure_exists(
            await self._route_plan_gateway.load(route_plan_id),
            "RoutePlan",
        )

        time_slot_label, start_time, end_time = await resolve_time_slot(
            self._time_slot_gateway, route_plan.time_slot_id
        )

        orders = await self._order_gateway.load_by_date(
            shop_id=route_plan.shop_id,
            delivery_date=route_plan.delivery_date,
            start_time=start_time,
            end_time=end_time,
        )

        routable, unroutable = sort_orders_by_sequence(
            orders, route_plan.order_sequence
        )

        shop = await self._shop_gateway.load_shop(route_plan.shop_id)
        shop_coords = CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
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
            delivery_date=route_plan.delivery_date.strftime("%d.%m.%Y"),
            time_slot=time_slot_label,
            ordered_orders=routable,
            unroutable_orders=unroutable,
            geometry=geometry,
        )
