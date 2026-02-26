from unittest.mock import AsyncMock, Mock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.services.tsp_solvers.route_optimizer import (
    HELD_KARP_THRESHOLD,
    RouteOptimizer,
)


@pytest.fixture()
def osrm():
    return AsyncMock()


@pytest.fixture()
def held_karp():
    solver = Mock()
    solver.solve.return_value = [0, 1, 2, 0]
    return solver


@pytest.fixture()
def pyvrp():
    solver = Mock()
    solver.solve.return_value = [0, 1, 2, 0]
    return solver


@pytest.fixture()
def optimizer(osrm, held_karp, pyvrp):
    return RouteOptimizer(
        osrm_client=osrm,
        held_karp=held_karp,
        pyvrp=pyvrp,
    )


def _make_order(order_id, has_coords=True):
    order = Mock()
    order.id = order_id
    if has_coords:
        order.delivery_address.coordinates.latitude = 50.0
        order.delivery_address.coordinates.longitude = 30.0
    else:
        order.delivery_address = None
    return order


def _make_matrix(n):
    return [[float(i != j) * 100 for j in range(n)] for i in range(n)]


class TestSolverSelection:
    @pytest.mark.asyncio()
    async def test_selects_held_karp_for_small_n(
        self, optimizer, osrm, held_karp, pyvrp
    ):
        orders = [_make_order(i) for i in range(5)]
        n = len(orders) + 1
        assert n <= HELD_KARP_THRESHOLD

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        held_karp.solve.assert_called_once()
        pyvrp.solve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_selects_pyvrp_for_large_n(
        self, optimizer, osrm, held_karp, pyvrp
    ):
        orders = [_make_order(i) for i in range(HELD_KARP_THRESHOLD)]
        n = len(orders) + 1
        assert n > HELD_KARP_THRESHOLD

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        pyvrp.solve.return_value = [0, *range(1, n), 0]
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        pyvrp.solve.assert_called_once()
        held_karp.solve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_returns_none_on_solver_failure(
        self, optimizer, osrm, held_karp
    ):
        orders = [_make_order(i) for i in range(3)]
        n = len(orders) + 1

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        held_karp.solve.side_effect = RuntimeError("boom")
        shop = Mock(latitude=50.0, longitude=30.0)

        result = await optimizer.compute(shop, orders)

        assert result is None


class TestUnreachableFiltering:
    @pytest.mark.asyncio()
    async def test_filters_unreachable_points(
        self, optimizer, osrm, held_karp
    ):
        inf = float("inf")
        matrix = [
            [0, 100, 100, 100, 100, inf],
            [100, 0, 100, 100, 100, inf],
            [100, 100, 0, 100, 100, inf],
            [100, 100, 100, 0, 100, inf],
            [100, 100, 100, 100, 0, inf],
            [inf, inf, inf, inf, inf, 0],
        ]
        orders = [_make_order(i) for i in range(5)]
        osrm.get_duration_matrix.return_value = matrix
        held_karp.solve.return_value = [0, 1, 2, 3, 4, 0]
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        called_matrix = held_karp.solve.call_args[0][0]
        assert len(called_matrix) == 5
        for row in called_matrix:
            assert float("inf") not in row

    @pytest.mark.asyncio()
    async def test_returns_none_when_all_unreachable(self, optimizer, osrm):
        inf = float("inf")
        matrix = [
            [0, inf, inf],
            [inf, 0, inf],
            [inf, inf, 0],
        ]
        orders = [_make_order(i) for i in range(2)]
        osrm.get_duration_matrix.return_value = matrix
        shop = Mock(latitude=50.0, longitude=30.0)

        result = await optimizer.compute(shop, orders)

        assert result is None


class TestEdgeCases:
    @pytest.mark.asyncio()
    async def test_returns_none_when_single_order(self, optimizer):
        order = _make_order(1)
        shop = Mock(latitude=50.0, longitude=30.0)

        result = await optimizer.compute(shop, [order])

        assert result is None

    @pytest.mark.asyncio()
    async def test_returns_none_when_no_coordinates(self, optimizer, osrm):
        orders = [_make_order(i, has_coords=False) for i in range(3)]
        shop = Mock(latitude=50.0, longitude=30.0)

        result = await optimizer.compute(shop, orders)

        assert result is None
        osrm.get_duration_matrix.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_returns_none_when_matrix_fails(self, optimizer, osrm):
        orders = [_make_order(i) for i in range(3)]
        osrm.get_duration_matrix.return_value = None
        shop = Mock(latitude=50.0, longitude=30.0)

        result = await optimizer.compute(shop, orders)

        assert result is None


class TestFindBestInsertionPosition:
    def test_empty_sequence_returns_zero(self):
        pos = RouteOptimizer.find_best_insertion_position(
            shop_coords=CoordinatesDTO(50.0, 30.0),
            existing_sequence_coords=[],
            new_point_coords=CoordinatesDTO(50.1, 30.1),
        )
        assert pos == 0

    def test_inserts_near_closest_point(self):
        shop = CoordinatesDTO(50.0, 30.0)
        existing = [
            CoordinatesDTO(50.1, 30.1),
            CoordinatesDTO(50.2, 30.2),
            CoordinatesDTO(50.3, 30.3),
        ]
        new_point = CoordinatesDTO(50.15, 30.15)

        pos = RouteOptimizer.find_best_insertion_position(
            shop_coords=shop,
            existing_sequence_coords=existing,
            new_point_coords=new_point,
        )

        assert 0 <= pos <= len(existing)
        assert pos == 1

    def test_single_point(self):
        shop = CoordinatesDTO(50.0, 30.0)
        existing = [CoordinatesDTO(50.5, 30.5)]
        new_point = CoordinatesDTO(50.6, 30.6)

        pos = RouteOptimizer.find_best_insertion_position(
            shop_coords=shop,
            existing_sequence_coords=existing,
            new_point_coords=new_point,
        )

        assert pos in {0, 1}
