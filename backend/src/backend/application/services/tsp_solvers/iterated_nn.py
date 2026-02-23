import logging

from backend.application.services.tsp_solvers.base import (
    local_search,
    route_cost,
)

logger = logging.getLogger(__name__)

MAX_STARTS = 30


class IteratedNNSolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        k = min(n, MAX_STARTS)
        logger.info("Iterated NN solver started: n=%d, starts=%d", n, k)

        if n <= 2:
            return [*range(n), 0]

        starts = _select_starts(matrix, n, k)

        best_route: list[int] = []
        best_cost = float("inf")

        for start in starts:
            route = _nearest_neighbor_from(matrix, n, start)
            route = local_search(route, matrix)
            cost = route_cost(route, matrix)
            if cost < best_cost:
                best_cost = cost
                best_route = route

        logger.info(
            "Iterated NN solver finished: n=%d, cost=%.1f", n, best_cost
        )
        return best_route


def _select_starts(matrix: list[list[float]], n: int, k: int) -> list[int]:
    if k >= n:
        return list(range(n))
    ranked = sorted(range(n), key=lambda i: matrix[0][i])
    return ranked[:k]


def _nearest_neighbor_from(
    matrix: list[list[float]],
    n: int,
    start: int,
) -> list[int]:
    visited = [False] * n
    visited[start] = True
    route = [start]
    current = start

    for _ in range(n - 1):
        best_next = -1
        best_cost = float("inf")
        for j in range(n):
            if not visited[j] and matrix[current][j] < best_cost:
                best_cost = matrix[current][j]
                best_next = j
        if best_next == -1:
            logger.error(
                "Nearest neighbor: unreachable nodes from node %d, "
                "visited %d/%d nodes",
                current,
                len(route),
                n,
            )
            break
        visited[best_next] = True
        route.append(best_next)
        current = best_next

    route.append(start)

    if start != 0:
        idx = route.index(0)
        route = route[idx:-1] + route[:idx] + [0]

    return route
