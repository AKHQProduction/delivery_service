import copy
import math
from unittest.mock import AsyncMock, Mock

import pytest

from backend.application.dto.coordinates import CoordinatesDTO, EdgeInput
from backend.application.services.edge_preference_collector import (
    PreferenceMap,
    build_preference_map,
    extract_edges,
)
from backend.application.services.tsp_solvers.route_optimizer import (
    RouteOptimizer,
)
from backend.infrastructure.tsp_solvers.held_karp import HeldKarpSolver


def _euclidean_matrix(coords: list[tuple[float, float]]) -> list[list[float]]:
    n = len(coords)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                matrix[i][j] = math.hypot(dx, dy) * 10_000
    return matrix


def _make_order(order_id, lat, lng):
    order = Mock()
    order.id = order_id
    order.delivery_address.coordinates = CoordinatesDTO(
        latitude=lat, longitude=lng
    )
    return order


def _ring_coords(n, center=(50.45, 30.52), radius=0.02):
    result = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        lat = round(center[0] + radius * math.cos(angle), 4)
        lng = round(center[1] + radius * math.sin(angle), 4)
        result.append((lat, lng))
    return result


def _mock_history_record(edge: EdgeInput, times_seen: int):
    record = Mock()
    record.from_coords = [
        edge.from_coords.latitude,
        edge.from_coords.longitude,
    ]
    record.to_coords = [edge.to_coords.latitude, edge.to_coords.longitude]
    record.times_seen = times_seen
    return record


def _make_optimizer():
    osrm = AsyncMock()
    optimizer = RouteOptimizer(
        osrm_client=osrm,
        held_karp=HeldKarpSolver(),
        pyvrp=Mock(),
    )
    return optimizer, osrm


def _cw_edge_count(route_ids, n_ring):
    count = 0
    for k in range(len(route_ids) - 1):
        a = route_ids[k] - 1
        b = route_ids[k + 1] - 1
        if (a + 1) % n_ring == b:
            count += 1
    return count


def _ccw_edge_count(route_ids, n_ring):
    count = 0
    for k in range(len(route_ids) - 1):
        a = route_ids[k] - 1
        b = route_ids[k + 1] - 1
        if (a - 1) % n_ring == b:
            count += 1
    return count


def _build_ring_prefs(ring, direction="cw"):
    prefs: PreferenceMap = {}
    n = len(ring)
    for i in range(n):
        nxt = (i + 1) % n if direction == "cw" else (i - 1) % n
        edge = EdgeInput(
            from_coords=CoordinatesDTO(ring[i][0], ring[i][1]),
            to_coords=CoordinatesDTO(ring[nxt][0], ring[nxt][1]),
        )
        prefs[edge] = 1.0
    return prefs


class TestPreferencesProof:
    @pytest.mark.asyncio()
    async def test_opposite_preferences_produce_different_routes(self):
        """10 orders on a symmetric ring — CW and CCW tours cost the same.

        CW preferences discount CW edges by 20% → solver picks CW.
        CCW preferences discount CCW edges → solver picks CCW.
        """
        n_orders = 10
        ring = _ring_coords(n_orders)
        shop_coord = (50.45, 30.52)

        shop = CoordinatesDTO(latitude=shop_coord[0], longitude=shop_coord[1])
        orders = [
            _make_order(i + 1, ring[i][0], ring[i][1]) for i in range(n_orders)
        ]
        base_matrix = _euclidean_matrix([shop_coord, *ring])

        optimizer, osrm = _make_optimizer()
        osrm.get_duration_matrix.side_effect = lambda _: copy.deepcopy(
            base_matrix
        )

        cw_route = await optimizer.compute(
            shop,
            orders,
            edge_preferences=_build_ring_prefs(ring, "cw"),
        )
        ccw_route = await optimizer.compute(
            shop,
            orders,
            edge_preferences=_build_ring_prefs(ring, "ccw"),
        )

        assert cw_route is not None
        assert ccw_route is not None
        assert cw_route != ccw_route

        assert _cw_edge_count(cw_route, n_orders) > _ccw_edge_count(
            cw_route,
            n_orders,
        )
        assert _ccw_edge_count(ccw_route, n_orders) > _cw_edge_count(
            ccw_route,
            n_orders,
        )

    @pytest.mark.asyncio()
    async def test_preferences_override_baseline(self):
        """Compute baseline without preferences.

        Add preferences for the OPPOSITE direction → route must change.
        """
        n_orders = 10
        ring = _ring_coords(n_orders)
        shop_coord = (50.45, 30.52)

        shop = CoordinatesDTO(latitude=shop_coord[0], longitude=shop_coord[1])
        orders = [
            _make_order(i + 1, ring[i][0], ring[i][1]) for i in range(n_orders)
        ]
        base_matrix = _euclidean_matrix([shop_coord, *ring])

        optimizer, osrm = _make_optimizer()
        osrm.get_duration_matrix.side_effect = lambda _: copy.deepcopy(
            base_matrix
        )

        baseline = await optimizer.compute(shop, orders, edge_preferences=None)
        assert baseline is not None

        is_cw = _cw_edge_count(baseline, n_orders) > _ccw_edge_count(
            baseline,
            n_orders,
        )
        opposite = "ccw" if is_cw else "cw"

        biased = await optimizer.compute(
            shop,
            orders,
            edge_preferences=_build_ring_prefs(ring, opposite),
        )
        assert biased is not None
        assert biased != baseline


class TestFullPipeline:
    @pytest.mark.asyncio()
    async def test_15_orders_extract_build_compute(self):
        n_orders = 15
        ring = _ring_coords(n_orders)
        shop_coord = (50.45, 30.52)

        shop = CoordinatesDTO(latitude=shop_coord[0], longitude=shop_coord[1])
        orders = [
            _make_order(i + 1, ring[i][0], ring[i][1]) for i in range(n_orders)
        ]

        # step 1: historical CW sequence → extract edges
        cw_sequence = list(range(1, n_orders + 1))
        edges = extract_edges(orders, cw_sequence)
        assert len(edges) == n_orders - 1

        # step 2: simulate DB history (seen 10-23 times)
        history = [
            _mock_history_record(e, times_seen=10 + i)
            for i, e in enumerate(edges)
        ]
        for edge in edges[:5]:
            reverse = EdgeInput(
                from_coords=edge.to_coords,
                to_coords=edge.from_coords,
            )
            history.append(_mock_history_record(reverse, times_seen=2))

        # step 3: build preference map
        pref_map = build_preference_map(history)
        assert len(pref_map) == len(history)

        forward_scores = [pref_map[e] for e in edges]
        assert all(s > 0.4 for s in forward_scores)

        # step 4-5: compute and compare
        base_matrix = _euclidean_matrix([shop_coord, *ring])
        optimizer, osrm = _make_optimizer()
        osrm.get_duration_matrix.side_effect = lambda _: copy.deepcopy(
            base_matrix
        )

        baseline = await optimizer.compute(shop, orders, edge_preferences=None)
        biased = await optimizer.compute(
            shop,
            orders,
            edge_preferences=pref_map,
        )

        assert baseline is not None
        assert biased is not None
        assert len(biased) == n_orders
        assert set(biased) == set(range(1, n_orders + 1))

        cw_biased = _cw_edge_count(biased, n_orders)
        cw_baseline = _cw_edge_count(baseline, n_orders)
        assert cw_biased >= cw_baseline

    @pytest.mark.asyncio()
    async def test_heavy_history_100_edges(self):
        """100 historical edges with times_seen from 1 to 100.

        Verify normalization: max→1.0, min→0.01, monotonic.
        """
        history = []
        for i in range(100):
            edge = EdgeInput(
                from_coords=CoordinatesDTO(50.0 + i * 0.001, 30.0 + i * 0.001),
                to_coords=CoordinatesDTO(
                    50.0 + (i + 1) * 0.001,
                    30.0 + (i + 1) * 0.001,
                ),
            )
            history.append(_mock_history_record(edge, times_seen=i + 1))

        pref_map = build_preference_map(history)

        assert len(pref_map) == 100

        scores = sorted(pref_map.values())
        assert scores[-1] == pytest.approx(1.0)
        assert scores[0] == pytest.approx(0.01)

        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1]

    @pytest.mark.asyncio()
    async def test_preferences_combined_with_unreachable(self):
        """12 orders, 2 unreachable (matrix has inf).

        Preferences apply to reachable subset. Unreachable appended at end.
        """
        n_orders = 12
        ring = _ring_coords(n_orders)
        shop_coord = (50.45, 30.52)

        shop = CoordinatesDTO(latitude=shop_coord[0], longitude=shop_coord[1])
        orders = [
            _make_order(i + 1, ring[i][0], ring[i][1]) for i in range(n_orders)
        ]

        matrix = _euclidean_matrix([shop_coord, *ring])

        inf = float("inf")
        for j in range(len(matrix)):
            if j != 11:
                matrix[11][j] = inf
                matrix[j][11] = inf
            if j != 12:
                matrix[12][j] = inf
                matrix[j][12] = inf

        prefs = _build_ring_prefs(ring[:10], "cw")

        optimizer, osrm = _make_optimizer()
        osrm.get_duration_matrix.return_value = matrix

        result = await optimizer.compute(shop, orders, edge_preferences=prefs)
        assert result is not None
        assert len(result) == n_orders
        assert set(result) == set(range(1, n_orders + 1))

        assert set(result[-2:]) == {11, 12}
