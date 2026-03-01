from datetime import date
from unittest.mock import Mock
from uuid import uuid4

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.services.route_builder import (
    build_route_read_model,
    create_route_plan,
    insert_order_into_route,
    remove_order_from_route,
    sort_orders_by_sequence,
    split_orders_by_coords,
)
from backend.application.vars import RoutePlanId, ShopId


def _make_order(
    order_id,
    street="вул. Тестова",
    house="1",
    lat=50.0,
    lon=30.0,
    has_coords=True,
    apartment=None,
    comment=None,
    payment_method="OTHER",
    delivery_phone="+380501234567",
):
    order = Mock()
    order.id = order_id
    order.comment = comment
    order.payment_method = payment_method
    order.delivery_phone = delivery_phone

    addr = Mock()
    addr.street = street
    addr.house = house
    addr.apartment = apartment

    if has_coords:
        addr.coordinates = CoordinatesDTO(latitude=lat, longitude=lon)
    else:
        addr.coordinates = None

    order.delivery_address = addr

    client = Mock()
    client.full_name = "Тест Клієнт"
    order.client = client

    item = Mock()
    item.name = "Вода 19л"
    item.quantity = 2
    item.price_per_item = 100
    order.items = [item]

    return order


class TestSortOrdersBySequence:
    def test_orders_sorted_by_sequence(self):
        o0, o1, o2 = _make_order(0), _make_order(1), _make_order(2)
        routable, unroutable = sort_orders_by_sequence([o0, o1, o2], [2, 0, 1])

        assert [o.id for o in routable] == [2, 0, 1]
        assert unroutable == []

    def test_unroutable_separated(self):
        o0 = _make_order(0, has_coords=False)
        routable, unroutable = sort_orders_by_sequence([o0], [0])

        assert routable == []
        assert [o.id for o in unroutable] == [0]

    def test_orders_not_in_sequence_appended(self):
        o0 = _make_order(0)
        o1 = _make_order(1)
        o2 = _make_order(2)
        routable, _ = sort_orders_by_sequence([o0, o1, o2], [0, 1])

        assert [o.id for o in routable] == [0, 1, 2]

    def test_stale_order_id_in_sequence_ignored(self):
        o0 = _make_order(0)
        o1 = _make_order(1)
        routable, _ = sort_orders_by_sequence([o0, o1], [0, 999, 1])

        assert [o.id for o in routable] == [0, 1]


class TestSplitOrdersByCoords:
    def test_split_routable_unroutable(self):
        o0 = _make_order(0)
        o1 = _make_order(1)
        o2 = _make_order(2, has_coords=False)
        routable, unroutable = split_orders_by_coords([o0, o1, o2])

        assert [o.id for o in routable] == [0, 1]
        assert [o.id for o in unroutable] == [2]

    def test_all_routable(self):
        o0, o1 = _make_order(0), _make_order(1)
        routable, unroutable = split_orders_by_coords([o0, o1])

        assert len(routable) == 2
        assert unroutable == []

    def test_all_unroutable(self):
        o0 = _make_order(0, has_coords=False)
        o1 = _make_order(1, has_coords=False)
        routable, unroutable = split_orders_by_coords([o0, o1])

        assert routable == []
        assert len(unroutable) == 2


class TestBuildRouteReadModel:
    def test_builds_model(self):
        from uuid import uuid4

        from backend.application.vars import RoutePlanId

        plan_id = RoutePlanId(uuid4())
        o0 = _make_order(uuid4(), street="Хрещатик", house="10")
        o1 = _make_order(uuid4(), street="Хрещатик", house="10")

        model = build_route_read_model(
            route_plan_id=plan_id,
            delivery_date="25.02.2026",
            time_slot=None,
            ordered_orders=[o0, o1],
            unroutable_orders=[],
        )

        assert model.route_plan_id == plan_id
        assert model.delivery_date == "25.02.2026"
        assert len(model.points) == 2
        assert model.points[0].sequence == 0
        assert model.points[1].sequence == 1
        assert model.stats.total_orders == 2
        assert model.stats.unique_addresses == 1

    def test_builds_model_with_time_slot(self):
        from uuid import uuid4

        from backend.application.vars import RoutePlanId

        plan_id = RoutePlanId(uuid4())
        o0 = _make_order(uuid4())

        model = build_route_read_model(
            route_plan_id=plan_id,
            delivery_date="25.02.2026",
            time_slot="09:00-14:00",
            ordered_orders=[o0],
            unroutable_orders=[],
        )

        assert model.time_slot == "09:00-14:00"


class TestCreateRoutePlan:
    def _make_gateway(self):
        gw = Mock()
        gw.next_id.return_value = RoutePlanId(uuid4())
        return gw

    def test_with_optimized_ids(self):
        gw = self._make_gateway()
        o0 = _make_order("a", lat=50.1, lon=30.1)
        o1 = _make_order("b", lat=50.2, lon=30.2)
        o2 = _make_order("c", has_coords=False)

        plan = create_route_plan(
            route_plan_gateway=gw,
            shop_id=ShopId(uuid4()),
            delivery_date=date(2026, 2, 25),
            time_slot_id=None,
            orders=[o0, o1, o2],
            optimized_ids=["b", "a"],
        )

        ids = plan.order_sequence
        assert ids[:2] == ["b", "a"]
        assert "c" in ids
        gw.save.assert_called_once_with(plan)

    def test_without_optimized_ids(self):
        gw = self._make_gateway()
        o0 = _make_order("a", lat=50.1, lon=30.1)
        o1 = _make_order("b", has_coords=False)

        plan = create_route_plan(
            route_plan_gateway=gw,
            shop_id=ShopId(uuid4()),
            delivery_date=date(2026, 2, 25),
            time_slot_id=None,
            orders=[o0, o1],
            optimized_ids=None,
        )

        ids = plan.order_sequence
        assert ids[0] == "a"
        assert ids[1] == "b"


def _make_route_plan(order_ids: list) -> Mock:
    plan = Mock()
    plan.id = RoutePlanId(uuid4())
    plan.order_sequence = list(order_ids)
    return plan


class TestRemoveOrderFromRoute:
    def test_remove_from_middle(self):
        plan = _make_route_plan(["a", "b", "c"])
        remove_order_from_route(plan, "b")
        assert plan.order_sequence == ["a", "c"]

    def test_remove_from_start(self):
        plan = _make_route_plan(["a", "b", "c"])
        remove_order_from_route(plan, "a")
        assert plan.order_sequence == ["b", "c"]

    def test_remove_from_end(self):
        plan = _make_route_plan(["a", "b", "c"])
        remove_order_from_route(plan, "c")
        assert plan.order_sequence == ["a", "b"]

    def test_remove_missing_order(self):
        plan = _make_route_plan(["a", "b"])
        remove_order_from_route(plan, "missing")
        assert plan.order_sequence == ["a", "b"]


class TestInsertOrderIntoRoute:
    def test_insert_with_coordinates(self):
        plan = _make_route_plan(["a", "c"])
        shop_coords = CoordinatesDTO(latitude=50.0, longitude=30.0)

        order_a = _make_order("a", lat=50.1, lon=30.1)
        order_b = _make_order("b", lat=50.15, lon=30.15)
        order_c = _make_order("c", lat=50.3, lon=30.3)

        insert_order_into_route(
            plan, order_b, shop_coords, [order_a, order_b, order_c]
        )

        assert "b" in plan.order_sequence
        assert len(plan.order_sequence) == 3

    def test_insert_without_coordinates_appends(self):
        plan = _make_route_plan(["a"])
        shop_coords = CoordinatesDTO(latitude=50.0, longitude=30.0)

        order_no_coords = _make_order("b", has_coords=False)

        insert_order_into_route(
            plan, order_no_coords, shop_coords, [order_no_coords]
        )

        assert plan.order_sequence == ["a", "b"]

    def test_insert_without_shop_coords_appends(self):
        plan = _make_route_plan(["a"])

        order = _make_order("b", lat=50.1, lon=30.1)

        insert_order_into_route(plan, order, None, [order])

        assert plan.order_sequence == ["a", "b"]
