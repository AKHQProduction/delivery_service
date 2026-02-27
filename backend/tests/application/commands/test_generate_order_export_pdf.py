from datetime import time as dt_time
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from backend.application.commands.generate_order_export_pdf import (
    GenerateOrderExportPDFCommand,
    GenerateOrderExportPDFCommandHandler,
)
from backend.application.vars import (
    ExportDocType,
    RoutingMode,
    ShopRole,
    today,
)

_START = dt_time(9, 0)
_END = dt_time(18, 0)


def _make_order(order_id=None):
    order = Mock()
    order.id = order_id or uuid4()
    order.delivery_start_time = _START
    order.delivery_end_time = _END
    return order


def _make_handler(*, route_plan=None):
    user = Mock(shop_id=uuid4(), role=ShopRole.MANAGER)
    idp = AsyncMock()
    idp.current_user.return_value = user

    shop = Mock()
    shop.id = user.shop_id
    shop.latitude = 50.45
    shop.longitude = 30.52
    shop.name = "Test Shop"

    shop_gateway = AsyncMock()
    shop_gateway.load_shop.return_value = shop

    order_gateway = AsyncMock()
    time_slot_gateway = AsyncMock()

    route_plan_gateway = AsyncMock()
    route_plan_gateway.load_by_date.return_value = route_plan

    pdf_generator = Mock()
    pdf_generator.build_order_list.return_value = b"%PDF-fake"

    pdf_storage = AsyncMock()
    pdf_storage.save.return_value = "file-123"

    route_optimizer = AsyncMock()

    handler = GenerateOrderExportPDFCommandHandler(
        idp=idp,
        order_gateway=order_gateway,
        shop_gateway=shop_gateway,
        time_slot_gateway=time_slot_gateway,
        route_plan_gateway=route_plan_gateway,
        pdf_generator=pdf_generator,
        pdf_storage=pdf_storage,
        route_optimizer=route_optimizer,
    )
    return handler, order_gateway, route_plan_gateway, route_optimizer


@pytest.mark.asyncio()
async def test_uses_existing_route_plan():
    o1, o2, o3 = _make_order(), _make_order(), _make_order()

    plan = Mock()
    plan.order_sequence = [o3.id, o1.id, o2.id]

    handler, order_gw, route_plan_gw, optimizer = _make_handler(
        route_plan=plan,
    )
    order_gw.load_by_date.return_value = [o1, o2, o3]

    await handler.handle(
        GenerateOrderExportPDFCommand(
            delivery_date=today(),
            doc_type=ExportDocType.ORDER_LIST,
            routing_mode=RoutingMode.OPTIMIZED,
        )
    )

    route_plan_gw.load_by_date.assert_awaited_once()
    optimizer.compute.assert_not_awaited()


@pytest.mark.asyncio()
async def test_falls_back_to_optimizer_when_no_plan():
    o1, o2 = _make_order(), _make_order()

    handler, order_gw, route_plan_gw, optimizer = _make_handler(
        route_plan=None,
    )
    order_gw.load_by_date.return_value = [o1, o2]
    optimizer.compute.return_value = [o2.id, o1.id]

    with patch("asyncio.get_running_loop") as mock_loop:
        mock_loop.return_value.run_in_executor = AsyncMock(
            return_value=b"%PDF-fake"
        )
        await handler.handle(
            GenerateOrderExportPDFCommand(
                delivery_date=today(),
                doc_type=ExportDocType.ORDER_LIST,
                routing_mode=RoutingMode.OPTIMIZED,
            )
        )

    route_plan_gw.load_by_date.assert_awaited_once()
    optimizer.compute.assert_awaited_once()


@pytest.mark.asyncio()
async def test_routing_mode_none_ignores_plan():
    o1, o2 = _make_order(), _make_order()

    handler, order_gw, route_plan_gw, optimizer = _make_handler()
    order_gw.load_by_date.return_value = [o1, o2]

    await handler.handle(
        GenerateOrderExportPDFCommand(
            delivery_date=today(),
            doc_type=ExportDocType.ORDER_LIST,
            routing_mode=RoutingMode.NONE,
        )
    )

    route_plan_gw.load_by_date.assert_not_awaited()
    optimizer.compute.assert_not_awaited()
