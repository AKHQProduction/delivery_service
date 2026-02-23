from unittest.mock import AsyncMock, Mock

import pytest

from backend.application.services.route_optimizer import (
    HELD_KARP_THRESHOLD,
    ORTOOLS_THRESHOLD,
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
def iterated_nn():
    solver = Mock()
    solver.solve.return_value = [0, 1, 2, 0]
    return solver


@pytest.fixture()
def ortools():
    solver = Mock()
    solver.solve.return_value = [0, 1, 2, 0]
    return solver


@pytest.fixture()
def fallback():
    solver = Mock()
    solver.solve.return_value = [0, 1, 2, 0]
    return solver


@pytest.fixture()
def optimizer(osrm, held_karp, iterated_nn, ortools, fallback):
    return RouteOptimizer(
        osrm_client=osrm,
        held_karp=held_karp,
        iterated_nn=iterated_nn,
        ortools=ortools,
        fallback=fallback,
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
        self, optimizer, osrm, held_karp, ortools
    ):
        orders = [_make_order(i) for i in range(5)]
        n = len(orders) + 1
        assert n <= HELD_KARP_THRESHOLD

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        held_karp.solve.assert_called_once()
        ortools.solve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_selects_iterated_nn_for_medium_n(
        self, optimizer, osrm, held_karp, iterated_nn, ortools
    ):
        orders = [_make_order(i) for i in range(HELD_KARP_THRESHOLD)]
        n = len(orders) + 1
        assert HELD_KARP_THRESHOLD < n <= ORTOOLS_THRESHOLD

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        iterated_nn.solve.return_value = [0, *range(1, n), 0]
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        iterated_nn.solve.assert_called_once()
        held_karp.solve.assert_not_called()
        ortools.solve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_selects_ortools_for_large_n(
        self, optimizer, osrm, held_karp, iterated_nn, ortools
    ):
        orders = [_make_order(i) for i in range(ORTOOLS_THRESHOLD)]
        n = len(orders) + 1
        assert n > ORTOOLS_THRESHOLD

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        ortools.solve.return_value = [0, *range(1, n), 0]
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        ortools.solve.assert_called_once()
        held_karp.solve.assert_not_called()
        iterated_nn.solve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_fallback_on_exception(
        self, optimizer, osrm, held_karp, fallback
    ):
        orders = [_make_order(i) for i in range(3)]
        n = len(orders) + 1

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        held_karp.solve.side_effect = RuntimeError("boom")
        shop = Mock(latitude=50.0, longitude=30.0)

        await optimizer.compute(shop, orders)

        held_karp.solve.assert_called_once()
        fallback.solve.assert_called_once()

    @pytest.mark.asyncio()
    async def test_returns_none_when_both_solvers_fail(
        self, optimizer, osrm, held_karp, fallback
    ):
        orders = [_make_order(i) for i in range(3)]
        n = len(orders) + 1

        osrm.get_duration_matrix.return_value = _make_matrix(n)
        held_karp.solve.side_effect = RuntimeError("boom")
        fallback.solve.side_effect = RuntimeError("fallback boom")
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
