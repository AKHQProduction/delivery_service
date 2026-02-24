import logging

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.services.tsp_solvers.base import TSPSolver
from backend.application.vars import OrderId
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.tsp_solvers.osrm import OSRMClient

logger = logging.getLogger(__name__)

HELD_KARP_THRESHOLD = 20
UNREACHABLE_RATIO = 0.3


class RouteOptimizer:
    def __init__(
        self,
        osrm_client: OSRMClient,
        held_karp: TSPSolver,
        pyvrp: TSPSolver,
    ) -> None:
        self._osrm = osrm_client
        self._held_karp = held_karp
        self._pyvrp = pyvrp

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

        matrix, coord_orders, unreachable = self._filter_unreachable(
            matrix,
            coord_orders,
        )
        without_coords.extend(unreachable)

        if not coord_orders:
            logger.error(
                "Route optimization skipped: all %d points are unreachable",
                len(orders),
            )
            return None

        n = len(matrix)
        solver = self._held_karp if n <= HELD_KARP_THRESHOLD else self._pyvrp

        try:
            route = solver.solve(matrix)
        except Exception as exc:
            logger.exception(
                "Solver %s failed [%s]",
                solver.__class__.__name__,
                exc.__class__.__name__,
            )
            return None

        index_map = {idx + 1: order for idx, order in enumerate(coord_orders)}
        optimized = [index_map[i].id for i in route if i in index_map]

        seen = set(optimized)
        optimized.extend(o.id for o in coord_orders if o.id not in seen)
        optimized.extend(o.id for o in without_coords)

        return optimized

    def _filter_unreachable(
        self,
        matrix: list[list[float]],
        coord_orders: list[Order],
    ) -> tuple[list[list[float]], list[Order], list[Order]]:
        n = len(matrix)
        inf = float("inf")

        bad_indices: set[int] = set()
        for i in range(1, n):
            inf_count = sum(
                1
                for j in range(n)
                if i != j and (matrix[i][j] == inf or matrix[j][i] == inf)
            )
            if inf_count / max(n - 1, 1) > UNREACHABLE_RATIO:
                bad_indices.add(i)

        if not bad_indices:
            return matrix, coord_orders, []

        logger.warning(
            "Dropping %d unreachable points from routing",
            len(bad_indices),
        )

        keep = [i for i in range(n) if i not in bad_indices]
        filtered_matrix = [[matrix[i][j] for j in keep] for i in keep]
        filtered_orders = [
            o
            for idx, o in enumerate(coord_orders)
            if (idx + 1) not in bad_indices
        ]
        unreachable_orders = [
            o for idx, o in enumerate(coord_orders) if (idx + 1) in bad_indices
        ]

        return filtered_matrix, filtered_orders, unreachable_orders
