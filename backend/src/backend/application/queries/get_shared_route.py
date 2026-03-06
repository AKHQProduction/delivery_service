import logging

from backend.application.common import ensure_exists
from backend.application.dto.gateways.route_gateway import RouteReadModel
from backend.application.services.route_builder import (
    build_route_read_model,
    resolve_time_slot,
    sort_orders_by_sequence,
)
from backend.application.vars import RoutePlanId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyTimeSlotGateway,
)

logger = logging.getLogger(__name__)


class GetSharedRouteQueryHandler:
    def __init__(
        self,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
    ) -> None:
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._time_slot_gateway = time_slot_gateway

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

        return build_route_read_model(
            route_plan_id=route_plan.id,
            delivery_date=route_plan.delivery_date.strftime("%d.%m.%Y"),
            time_slot=time_slot_label,
            time_slot_id=route_plan.time_slot_id,
            ordered_orders=routable,
            unroutable_orders=unroutable,
        )
