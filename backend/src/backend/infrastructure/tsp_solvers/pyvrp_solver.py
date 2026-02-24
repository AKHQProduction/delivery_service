import logging

from pyvrp import Client, Depot, Model
from pyvrp.stop import MaxRuntime, MultipleCriteria, NoImprovement

from backend.application.services.tsp_solvers.base import TSPSolver

logger = logging.getLogger(__name__)

DURATION_SCALE = 10
MAX_RUNTIME_SECONDS = 30
MIN_NO_IMPROVEMENT = 1000
NO_IMPROVEMENT_PER_NODE = 200


class PyVRPSolver(TSPSolver):
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info("PyVRP solver started: n=%d", n)

        if n <= 2:
            return [*range(n), 0]

        int_matrix = self._to_int_matrix(matrix)
        route = self._solve(int_matrix, n)

        cost = sum(
            matrix[route[i]][route[i + 1]] for i in range(len(route) - 1)
        )
        logger.info("PyVRP solver finished: n=%d, cost=%.1f", n, cost)
        return route

    def _to_int_matrix(self, matrix: list[list[float]]) -> list[list[int]]:
        return [[round(v * DURATION_SCALE) for v in row] for row in matrix]

    def _solve(self, int_matrix: list[list[int]], n: int) -> list[int]:
        m = Model()

        depot = m.add_depot(x=0, y=0)
        clients = [m.add_client(x=i, y=0, delivery=[1]) for i in range(1, n)]
        locations: list[Client | Depot] = [depot, *clients]

        m.add_vehicle_type(num_available=1, capacity=[n])

        for frm in range(n):
            for to in range(n):
                m.add_edge(
                    locations[frm],
                    locations[to],
                    distance=int_matrix[frm][to],
                    duration=int_matrix[frm][to],
                )

        no_improve_limit = max(MIN_NO_IMPROVEMENT, n * NO_IMPROVEMENT_PER_NODE)
        stop = MultipleCriteria([
            MaxRuntime(MAX_RUNTIME_SECONDS),
            NoImprovement(no_improve_limit),
        ])

        result = m.solve(stop=stop, display=False)

        if not result.is_feasible():
            msg = "PyVRP failed to find feasible solution: n=%d"
            raise RuntimeError(msg % n)

        routes = result.best.routes()
        if not routes:
            msg = "PyVRP returned no routes: n=%d"
            raise RuntimeError(msg % n)

        visits = list(routes[0].visits())
        return [0, *visits, 0]
