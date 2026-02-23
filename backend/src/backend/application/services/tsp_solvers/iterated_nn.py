import logging

from backend.application.services.tsp_solvers.base import route_cost, two_opt

logger = logging.getLogger(__name__)


class IteratedNNSolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info("Iterated NN+2opt solver started: n=%d", n)

        if n <= 2:
            return [*list(range(n)), 0]

        best_route: list[int] = []
        best_cost = float("inf")

        for start in range(n):
            route = _nearest_neighbor_from(matrix, n, start)
            route = two_opt(route, matrix)
            cost = route_cost(route, matrix)
            if cost < best_cost:
                best_cost = cost
                best_route = route

        logger.info(
            "Iterated NN+2opt solver finished: n=%d, cost=%.1f", n, best_cost
        )
        return best_route


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
            break
        visited[best_next] = True
        route.append(best_next)
        current = best_next

    route.append(start)

    if start != 0:
        idx = route.index(0)
        route = route[idx:-1] + route[:idx] + [0]

    return route
