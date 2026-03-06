import logging
from dataclasses import dataclass
from datetime import date

from backend.application.dto.gateways.route_gateway import RouteReadModel
from backend.application.policies.access import ensure_can_manage
from backend.application.services.route_builder import (
    build_route_read_model,
    resolve_time_slot,
    sort_orders_by_sequence,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyTimeSlotGateway,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetRoutesQuery:
    delivery_date: date


class GetRoutesQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._route_plan_gateway = route_plan_gateway
        self._time_slot_gateway = time_slot_gateway

    async def handle(self, query: GetRoutesQuery) -> list[RouteReadModel]:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        route_plans = await self._route_plan_gateway.load_all_by_date(
            shop_id=current_user.shop_id,
            delivery_date=query.delivery_date,
        )

        results: list[RouteReadModel] = []
        for route_plan in route_plans:
            time_slot_label, start_time, end_time = await resolve_time_slot(
                self._time_slot_gateway, route_plan.time_slot_id
            )

            orders = await self._order_gateway.load_by_date(
                shop_id=current_user.shop_id,
                delivery_date=query.delivery_date,
                start_time=start_time,
                end_time=end_time,
            )
            if not orders:
                continue

            routable, unroutable = sort_orders_by_sequence(
                orders, route_plan.order_sequence
            )

            results.append(
                build_route_read_model(
                    route_plan_id=route_plan.id,
                    delivery_date=query.delivery_date.strftime("%d.%m.%Y"),
                    time_slot=time_slot_label,
                    time_slot_id=route_plan.time_slot_id,
                    ordered_orders=routable,
                    unroutable_orders=unroutable,
                )
            )

        return results
