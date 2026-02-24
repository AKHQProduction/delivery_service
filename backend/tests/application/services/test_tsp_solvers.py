import pytest

from backend.infrastructure.tsp_solvers import HeldKarpSolver, PyVRPSolver

SIMPLE_MATRIX = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0],
]
OPTIMAL_COST = 80

ASYMMETRIC_MATRIX = [
    [0, 5, 100, 10],
    [100, 0, 5, 100],
    [100, 100, 0, 5],
    [5, 100, 100, 0],
]
ASYMMETRIC_OPTIMAL_COST = 20

TWO_POINT_MATRIX = [
    [0, 42],
    [42, 0],
]

INF = float("inf")
INF_MATRIX = [
    [0, 10, INF, 50],
    [10, 0, 20, INF],
    [INF, 20, 0, 15],
    [50, INF, 15, 0],
]


def _route_cost(route: list[int], matrix: list[list[float]]) -> float:
    return sum(matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))


@pytest.fixture()
def held_karp():
    return HeldKarpSolver()


@pytest.fixture()
def pyvrp():
    return PyVRPSolver()


class TestHeldKarpSolver:
    def test_returns_cyclic_route(self, held_karp):
        route = held_karp.solve(SIMPLE_MATRIX)
        assert route[0] == 0
        assert route[-1] == 0

    def test_visits_all_nodes(self, held_karp):
        route = held_karp.solve(SIMPLE_MATRIX)
        assert set(route) == {0, 1, 2, 3}

    def test_finds_optimal_cost(self, held_karp):
        route = held_karp.solve(SIMPLE_MATRIX)
        assert _route_cost(route, SIMPLE_MATRIX) == OPTIMAL_COST

    def test_handles_asymmetric_matrix(self, held_karp):
        route = held_karp.solve(ASYMMETRIC_MATRIX)
        assert _route_cost(route, ASYMMETRIC_MATRIX) == ASYMMETRIC_OPTIMAL_COST

    def test_two_point_matrix(self, held_karp):
        route = held_karp.solve(TWO_POINT_MATRIX)
        assert route[0] == 0
        assert route[-1] == 0
        assert set(route) == {0, 1}

    def test_matrix_with_inf(self, held_karp):
        route = held_karp.solve(INF_MATRIX)
        assert route[0] == 0
        assert route[-1] == 0
        assert set(route) == {0, 1, 2, 3}
        assert _route_cost(route, INF_MATRIX) < INF


class TestPyVRPSolver:
    def test_returns_cyclic_route(self, pyvrp):
        route = pyvrp.solve(SIMPLE_MATRIX)
        assert route[0] == 0
        assert route[-1] == 0

    def test_visits_all_nodes(self, pyvrp):
        route = pyvrp.solve(SIMPLE_MATRIX)
        assert set(route) == {0, 1, 2, 3}

    def test_finds_optimal_cost(self, pyvrp):
        route = pyvrp.solve(SIMPLE_MATRIX)
        assert _route_cost(route, SIMPLE_MATRIX) == OPTIMAL_COST

    def test_handles_asymmetric_matrix(self, pyvrp):
        route = pyvrp.solve(ASYMMETRIC_MATRIX)
        assert _route_cost(route, ASYMMETRIC_MATRIX) == ASYMMETRIC_OPTIMAL_COST

    def test_two_point_matrix(self, pyvrp):
        route = pyvrp.solve(TWO_POINT_MATRIX)
        assert route[0] == 0
        assert route[-1] == 0
        assert set(route) == {0, 1}
