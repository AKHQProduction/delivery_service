import logging

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from backend.application.services.tsp_solvers.base import TSPSolver

logger = logging.getLogger(__name__)

TIME_LIMIT_SECONDS = 15
INF_REPLACEMENT = 10**7


class ORToolsSolver(TSPSolver):
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info(
            "OR-Tools solver started: n=%d, time_limit=%ds",
            n,
            TIME_LIMIT_SECONDS,
        )

        if n <= 2:
            return [*range(n), 0]

        int_matrix = [
            [INF_REPLACEMENT if v == float("inf") else round(v) for v in row]
            for row in matrix
        ]

        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index: int, to_index: int) -> int:
            return int_matrix[manager.IndexToNode(from_index)][
                manager.IndexToNode(to_index)
            ]

        transit_id = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_id)

        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
        )
        search_params.time_limit.seconds = TIME_LIMIT_SECONDS

        solution = routing.SolveWithParameters(search_params)
        if solution is None:
            logger.error(
                "OR-Tools failed to find solution: n=%d, time_limit=%ds",
                n,
                TIME_LIMIT_SECONDS,
            )
            msg = "OR-Tools failed to find a solution"
            raise RuntimeError(msg)

        route: list[int] = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(0)

        cost = solution.ObjectiveValue()
        logger.info("OR-Tools solver finished: n=%d, cost=%d", n, cost)
        return route
