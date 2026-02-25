from datetime import date, time
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from backend.application.commands.create_order import CreateOrderCommandHandler
from backend.application.vars import OrderId, ShopId, TimeSlotId


def _make_order(order_id, lat=50.0, lon=30.0, has_coords=True):
    order = Mock()
    order.id = order_id
    order.date = date(2026, 3, 1)

    if has_coords:
        order.delivery_address.coordinates.latitude = lat
        order.delivery_address.coordinates.longitude = lon
    else:
        order.delivery_address.coordinates = None

    return order


def _make_handler(
    route_plan=None,
    existing_orders=None,
    shop_lat=50.45,
    shop_lon=30.52,
):
    handler = CreateOrderCommandHandler.__new__(CreateOrderCommandHandler)

    handler._route_plan_gateway = AsyncMock()
    handler._route_plan_gateway.load_by_date.return_value = route_plan
    handler._route_plan_gateway.next_id = Mock(return_value=uuid4())
    handler._route_plan_gateway.save = Mock()

    handler._order_gateway = AsyncMock()
    handler._order_gateway.load_by_date.return_value = existing_orders or []

    shop = Mock()
    shop.latitude = shop_lat
    shop.longitude = shop_lon
    handler._shop_gateway = AsyncMock()
    handler._shop_gateway.load_shop.return_value = shop

    handler._route_optimizer = AsyncMock()
    handler._route_optimizer.compute.return_value = None

    return handler


class TestAutoInsertNoExistingPlan:
    @pytest.mark.asyncio()
    async def test_skips_when_fewer_than_two_orders(self):
        handler = _make_handler(
            route_plan=None, existing_orders=[_make_order(1)]
        )
        order = _make_order(OrderId(uuid4()))

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(9, 0),
            end_time=time(14, 0),
        )

        handler._route_plan_gateway.save.assert_not_called()

    @pytest.mark.asyncio()
    async def test_creates_route_plan_with_two_or_more_orders(self):
        orders = [_make_order(1), _make_order(2)]
        handler = _make_handler(route_plan=None, existing_orders=orders)
        order = _make_order(OrderId(uuid4()))

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(9, 0),
            end_time=time(14, 0),
        )

        handler._route_plan_gateway.save.assert_called_once()

    @pytest.mark.asyncio()
    async def test_load_by_date_filters_by_time_slot(self):
        orders = [_make_order(1), _make_order(2)]
        handler = _make_handler(route_plan=None, existing_orders=orders)
        order = _make_order(OrderId(uuid4()))

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(9, 0),
            end_time=time(14, 0),
        )

        call_kwargs = handler._order_gateway.load_by_date.call_args
        assert call_kwargs.kwargs["start_time"] == time(9, 0)
        assert call_kwargs.kwargs["end_time"] == time(14, 0)


class TestAutoInsertExistingPlan:
    @pytest.mark.asyncio()
    async def test_order_with_coords_inserted_at_best_position(self):
        route_plan = Mock()
        route_plan.order_sequence = [1, 2]

        existing = [
            _make_order(1, lat=50.46, lon=30.53),
            _make_order(2, lat=50.47, lon=30.54),
        ]
        handler = _make_handler(
            route_plan=route_plan, existing_orders=existing
        )

        new_order = _make_order(3, lat=50.465, lon=30.535)

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=new_order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(9, 0),
            end_time=time(14, 0),
        )

        assert 3 in route_plan.order_sequence

    @pytest.mark.asyncio()
    async def test_order_without_coords_appended_to_end(self):
        route_plan = Mock()
        route_plan.order_sequence = [1, 2]
        handler = _make_handler(route_plan=route_plan)

        new_order = _make_order(3, has_coords=False)

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=new_order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(9, 0),
            end_time=time(14, 0),
        )

        assert route_plan.order_sequence[-1] == 3

    @pytest.mark.asyncio()
    async def test_existing_plan_load_by_date_filters_by_time_slot(self):
        route_plan = Mock()
        route_plan.order_sequence = [1]

        existing = [_make_order(1, lat=50.46, lon=30.53)]
        handler = _make_handler(
            route_plan=route_plan, existing_orders=existing
        )

        new_order = _make_order(2, lat=50.47, lon=30.54)

        await handler._auto_insert_into_route(
            shop_id=ShopId(uuid4()),
            order=new_order,
            time_slot_id=TimeSlotId(uuid4()),
            start_time=time(14, 0),
            end_time=time(21, 0),
        )

        call_kwargs = handler._order_gateway.load_by_date.call_args
        assert call_kwargs.kwargs["start_time"] == time(14, 0)
        assert call_kwargs.kwargs["end_time"] == time(21, 0)
