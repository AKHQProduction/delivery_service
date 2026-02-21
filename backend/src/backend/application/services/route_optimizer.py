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
            return None

        matrix = await self._osrm.get_duration_matrix(coordinates)
        if matrix is None:
            return None

        route = _nearest_neighbor(matrix)
        route = _three_opt(route, matrix)

        index_map = {idx + 1: order for idx, order in enumerate(coord_orders)}
        optimized = [index_map[i].id for i in route if i in index_map]

        seen = set(optimized)
        optimized.extend(o.id for o in coord_orders if o.id not in seen)
        optimized.extend(o.id for o in without_coords)

        return optimized


def _nearest_neighbor(matrix: list[list[float]]) -> list[int]:
    n = len(matrix)
    visited = [False] * n
    visited[0] = True
    route = [0]
    current = 0

    for _ in range(n - 1):
        best_next = -1
        best_cost = float("inf")
        for j in range(n):
            if not visited[j] and matrix[current][j] < best_cost:
                best_cost = matrix[current][j]
                best_next = j
        if best_next == -1:
            break
        visited[best_next] = True
        route.append(best_next)
        current = best_next

    return route


def _route_cost(route: list[int], matrix: list[list[float]]) -> float:
    return sum(matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))


def _three_opt(route: list[int], matrix: list[list[float]]) -> list[int]:
    n = len(route)
    if n < 5:
        return route

    best_cost = _route_cost(route, matrix)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 3):
            for j in range(i + 1, n - 2):
                for k in range(j + 1, n - 1):
                    route, best_cost, changed = _try_three_opt(
                        route, matrix, best_cost, i, j, k
                    )
                    if changed:
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break

    return route


def _try_three_opt(
    route: list[int],
    matrix: list[list[float]],
    best_cost: float,
    i: int,
    j: int,
    k: int,
) -> tuple[list[int], float, bool]:
    seg1 = route[:i]
    seg2 = route[i:j]
    seg3 = route[j:k]
    seg4 = route[k:]

    for candidate in (
        seg1 + seg2[::-1] + seg3 + seg4,
        seg1 + seg2 + seg3[::-1] + seg4,
        seg1 + seg2[::-1] + seg3[::-1] + seg4,
        seg1 + seg3 + seg2 + seg4,
        seg1 + seg3 + seg2[::-1] + seg4,
        seg1 + seg3[::-1] + seg2 + seg4,
        seg1 + seg3[::-1] + seg2[::-1] + seg4,
    ):
        cost = _route_cost(candidate, matrix)
        if cost < best_cost - 1e-10:
            return candidate, cost, True

    return route, best_cost, False
