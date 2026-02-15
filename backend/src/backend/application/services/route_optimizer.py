import logging

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import OrderId
from backend.infrastructure.osrm import OSRMClient
from backend.infrastructure.persistence.tables.orders import Order

logger = logging.getLogger(__name__)


class RouteOptimizer:
    def __init__(self, osrm_client: OSRMClient) -> None:
        self._osrm = osrm_client

    async def compute(
        self,
        shop_location: CoordinatesDTO,
        orders: list[Order],
        roundtrip: bool = True,
    ) -> list[OrderId] | None:
        if len(orders) <= 1:
            return None

        with_coords: list[tuple[int, Order]] = []
        without_coords: list[Order] = []

        for i, order in enumerate(orders):
            addr = order.delivery_address
            if addr and addr.coordinates:
                with_coords.append((i, order))
            else:
                without_coords.append(order)

        if not with_coords:
            return None

        waypoints: list[CoordinatesDTO] = [
            o.delivery_address.coordinates
            for _, o in with_coords
            if o.delivery_address.coordinates is not None
        ]

        result = await self._osrm.optimize_route(
            shop=shop_location,
            waypoints=waypoints,
            roundtrip=roundtrip,
        )
        if result is None:
            return None

        optimized = [with_coords[idx][1].id for idx in result.waypoint_order]
        optimized.extend(o.id for o in without_coords)

        return optimized
