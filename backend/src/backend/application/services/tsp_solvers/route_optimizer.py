import logging

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.services.tsp_solvers.base import TSPSolver
from backend.application.vars import OrderId
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.tsp_solvers.osrm import OSRMClient

logger = logging.getLogger(__name__)

HELD_KARP_THRESHOLD = 20
ORTOOLS_THRESHOLD = 80


class RouteOptimizer:
    def __init__(
        self,
        osrm_client: OSRMClient,
        held_karp: TSPSolver,
        iterated_nn: TSPSolver,
        ortools: TSPSolver,
        fallback: TSPSolver,
    ) -> None:
        self._osrm = osrm_client
        self._held_karp = held_karp
        self._iterated_nn = iterated_nn
        self._ortools = ortools
        self._fallback = fallback

    async def compute(
        self,
        shop_location: CoordinatesDTO,
        orders: list[Order],
    ) -> list[OrderId] | None:
        if len(orders) <= 1:
            return None

        coordinates: list[tuple[float, float]] = [
            (shop_location.latitude, shop_location.longitude),
        ]
        coord_orders: list[Order] = []
        without_coords: list[Order] = []

        for order in orders:
            addr = order.delivery_address
            if addr and addr.coordinates:
                coord_orders.append(order)
                coordinates.append((
                    addr.coordinates.latitude,
                    addr.coordinates.longitude,
                ))
            else:
                without_coords.append(order)

        if not coord_orders:
            logger.error(
                "Route optimization skipped: "
                "none of %d orders have coordinates",
                len(orders),
            )
            return None

        matrix = await self._osrm.get_duration_matrix(coordinates)
        if matrix is None:
            logger.error(
                "Route optimization failed: "
                "OSRM matrix unavailable for %d points",
                len(coordinates),
            )
            return None

        n = len(matrix)
        if n <= HELD_KARP_THRESHOLD:
            solver = self._held_karp
        elif n <= ORTOOLS_THRESHOLD:
            solver = self._iterated_nn
        else:
            solver = self._ortools

        try:
            route = solver.solve(matrix)
        except Exception as exc:
            logger.exception(
                "Solver %s failed [%s], using fallback",
                solver.__class__.__name__,
                exc.__class__.__name__,
            )
            try:
                route = self._fallback.solve(matrix)
            except Exception as fallback_exc:
                logger.exception(
                    "Fallback solver also failed [%s]",
                    fallback_exc.__class__.__name__,
                )
                return None

        index_map = {idx + 1: order for idx, order in enumerate(coord_orders)}
        optimized = [index_map[i].id for i in route if i in index_map]

        seen = set(optimized)
        optimized.extend(o.id for o in coord_orders if o.id not in seen)
        optimized.extend(o.id for o in without_coords)

        return optimized
