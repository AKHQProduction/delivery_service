import logging
import random

from backend.application.services.tsp_solvers.base import route_cost, two_opt

logger = logging.getLogger(__name__)

ALPHA = 1.0
BETA = 3.0
EVAPORATION = 0.3
NUM_RESTARTS = 3


class AntColonySolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        num_ants = n
        num_iterations = n * 5

        logger.info(
            "ACO solver started: n=%d, ants=%d, iterations=%d, restarts=%d",
            n,
            num_ants,
            num_iterations,
            NUM_RESTARTS,
        )

        if n <= 2:
            return [*list(range(n)), 0]

        q = _compute_q(matrix, n)
        eta = [
            [
                1.0 / max(matrix[i][j], 1e-10) if i != j else 0.0
                for j in range(n)
            ]
            for i in range(n)
        ]

        best_route: list[int] = []
        best_cost = float("inf")

        for _restart in range(NUM_RESTARTS):
            pheromone = _init_pheromone(matrix, n, q)

            run_best_route: list[int] = []
            run_best_cost = float("inf")

            for _ in range(num_iterations):
                for _ in range(num_ants):
                    route = _build_route(n, pheromone, eta)
                    cost = route_cost(route, matrix)
                    if cost < run_best_cost:
                        run_best_cost = cost
                        run_best_route = route

                for i in range(n):
                    for j in range(n):
                        pheromone[i][j] *= 1 - EVAPORATION

                deposit = q / run_best_cost
                for k in range(len(run_best_route) - 1):
                    i, j = run_best_route[k], run_best_route[k + 1]
                    pheromone[i][j] += deposit
                    pheromone[j][i] += deposit

            run_best_route = two_opt(run_best_route, matrix)
            run_best_cost = route_cost(run_best_route, matrix)

            if run_best_cost < best_cost:
                best_cost = run_best_cost
                best_route = run_best_route

        logger.info("ACO solver finished: n=%d, cost=%.1f", n, best_cost)
        return best_route


def _init_pheromone(
    matrix: list[list[float]],
    n: int,
    q: float,
) -> list[list[float]]:
    pheromone = [[1.0] * n for _ in range(n)]

    nn_route = _nearest_neighbor(matrix, n)
    nn_cost = route_cost(nn_route, matrix)
    deposit = q / nn_cost
    for k in range(len(nn_route) - 1):
        i, j = nn_route[k], nn_route[k + 1]
        pheromone[i][j] += deposit
        pheromone[j][i] += deposit

    return pheromone


def _nearest_neighbor(matrix: list[list[float]], n: int) -> list[int]:
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

    route.append(0)
    return route


def _compute_q(matrix: list[list[float]], n: int) -> float:
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j and matrix[i][j] != float("inf"):
                total += matrix[i][j]
                count += 1
    avg = total / max(count, 1)
    return avg * n


def _build_route(
    n: int,
    pheromone: list[list[float]],
    eta: list[list[float]],
) -> list[int]:
    visited = [False] * n
    visited[0] = True
    route = [0]
    current = 0

    for _ in range(n - 1):
        probabilities = []
        candidates = []
        for j in range(n):
            if not visited[j]:
                p = (pheromone[current][j] ** ALPHA) * (
                    eta[current][j] ** BETA
                )
                probabilities.append(p)
                candidates.append(j)

        if not candidates:
            break

        total = sum(probabilities)
        if total == 0:
            next_node = random.choice(candidates)  # noqa: S311
        else:
            r = random.random() * total  # noqa: S311
            cumulative = 0.0
            next_node = candidates[-1]
            for idx, p in enumerate(probabilities):
                cumulative += p
                if cumulative >= r:
                    next_node = candidates[idx]
                    break

        visited[next_node] = True
        route.append(next_node)
        current = next_node

    route.append(0)
    return route
