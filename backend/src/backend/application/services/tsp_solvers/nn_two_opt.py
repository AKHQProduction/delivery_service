import logging

from backend.application.services.tsp_solvers.base import route_cost, two_opt

logger = logging.getLogger(__name__)


class NNTwoOptSolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info("NN+2opt solver started: n=%d", n)

        route = _nearest_neighbor(matrix)
        nn_cost = route_cost([*route, 0], matrix)

        route.append(0)
        route = two_opt(route, matrix)
        final_cost = route_cost(route, matrix)

        logger.info(
            "NN+2opt solver finished: n=%d, nn_cost=%.1f, final_cost=%.1f",
            n,
            nn_cost,
            final_cost,
        )
        return route


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
