from unittest.mock import Mock

from backend.application.dto.coordinates import CoordinatesDTO, EdgeInput
from backend.application.services.edge_preference_collector import (
    build_preference_map,
    extract_edges,
)


def _make_order(order_id, lat=None, lng=None):
    order = Mock()
    order.id = order_id

    if lat is not None and lng is not None:
        addr = Mock()
        addr.coordinates = CoordinatesDTO(latitude=lat, longitude=lng)
        order.delivery_address = addr
    else:
        addr = Mock()
        addr.coordinates = None
        order.delivery_address = addr

    return order


class TestExtractEdges:
    def test_normal_sequence(self):
        o1 = _make_order("a", lat=50.1, lng=30.1)
        o2 = _make_order("b", lat=50.2, lng=30.2)
        o3 = _make_order("c", lat=50.3, lng=30.3)

        edges = extract_edges([o1, o2, o3], ["a", "b", "c"])

        assert len(edges) == 2
        assert edges[0] == EdgeInput(
            from_coords=CoordinatesDTO(50.1, 30.1),
            to_coords=CoordinatesDTO(50.2, 30.2),
        )
        assert edges[1] == EdgeInput(
            from_coords=CoordinatesDTO(50.2, 30.2),
            to_coords=CoordinatesDTO(50.3, 30.3),
        )

    def test_skips_no_coords(self):
        o1 = _make_order("a", lat=50.1, lng=30.1)
        o2 = _make_order("b")
        o3 = _make_order("c", lat=50.3, lng=30.3)

        edges = extract_edges([o1, o2, o3], ["a", "b", "c"])

        assert len(edges) == 1
        assert edges[0] == EdgeInput(
            from_coords=CoordinatesDTO(50.1, 30.1),
            to_coords=CoordinatesDTO(50.3, 30.3),
        )

    def test_single_order(self):
        o1 = _make_order("a", lat=50.1, lng=30.1)
        edges = extract_edges([o1], ["a"])
        assert edges == []

    def test_empty_sequence(self):
        o1 = _make_order("a", lat=50.1, lng=30.1)
        edges = extract_edges([o1], [])
        assert edges == []


class TestBuildPreferenceMap:
    def test_normalizes(self):
        e1 = Mock(
            from_coords=[50.1, 30.1],
            to_coords=[50.2, 30.2],
            times_seen=10,
        )
        e2 = Mock(
            from_coords=[50.2, 30.2],
            to_coords=[50.3, 30.3],
            times_seen=5,
        )
        e3 = Mock(
            from_coords=[50.3, 30.3],
            to_coords=[50.1, 30.1],
            times_seen=2,
        )

        pref_map = build_preference_map([e1, e2, e3])

        key1 = EdgeInput(
            from_coords=CoordinatesDTO(50.1, 30.1),
            to_coords=CoordinatesDTO(50.2, 30.2),
        )
        key2 = EdgeInput(
            from_coords=CoordinatesDTO(50.2, 30.2),
            to_coords=CoordinatesDTO(50.3, 30.3),
        )
        key3 = EdgeInput(
            from_coords=CoordinatesDTO(50.3, 30.3),
            to_coords=CoordinatesDTO(50.1, 30.1),
        )

        assert pref_map[key1] == 1.0
        assert pref_map[key2] == 0.5
        assert pref_map[key3] == 0.2

    def test_all_equal_times_seen(self):
        records = [
            Mock(
                from_coords=[50.1, 30.1],
                to_coords=[50.2, 30.2],
                times_seen=1,
            ),
            Mock(
                from_coords=[50.2, 30.2],
                to_coords=[50.3, 30.3],
                times_seen=1,
            ),
        ]
        pref_map = build_preference_map(records)
        assert len(pref_map) == 2
        assert all(score == 1.0 for score in pref_map.values())

    def test_empty(self):
        pref_map = build_preference_map([])
        assert pref_map == {}
