from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from backend.application.commands.reorder_route import (
    ReorderRouteCommand,
    ReorderRouteCommandHandler,
)
from backend.application.vars import ShopRole, today


def _make_handler(*, edge_gateway=None):
    user = Mock(shop_id=uuid4(), role=ShopRole.MANAGER)
    idp = AsyncMock()
    idp.current_user.return_value = user

    order_ids = [uuid4(), uuid4(), uuid4()]

    route_plan = Mock()
    route_plan.order_sequence = list(order_ids)

    route_plan_gateway = AsyncMock()
    route_plan_gateway.load_by_date.return_value = route_plan

    if edge_gateway is None:
        edge_gateway = AsyncMock()

    order_gateway = AsyncMock()
    order_gateway.load_by_date.return_value = []

    time_slot_gateway = AsyncMock()
    tr_manager = AsyncMock()

    handler = ReorderRouteCommandHandler(
        idp=idp,
        order_gateway=order_gateway,
        route_plan_gateway=route_plan_gateway,
        route_edge_history_gateway=edge_gateway,
        time_slot_gateway=time_slot_gateway,
        tr_manager=tr_manager,
    )
    return handler, tr_manager, route_plan, order_ids


@pytest.mark.asyncio()
async def test_commit_called_when_edge_history_fails():
    edge_gw = AsyncMock()
    edge_gw.upsert_edges.side_effect = RuntimeError("DB error")

    handler, tr_manager, route_plan, order_ids = _make_handler(
        edge_gateway=edge_gw,
    )

    await handler.handle(
        ReorderRouteCommand(
            delivery_date=today(),
            order_id=order_ids[0],
            new_position=2,
        )
    )

    tr_manager.commit.assert_awaited_once()
    assert order_ids[0] in route_plan.order_sequence
