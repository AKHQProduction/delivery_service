import uuid
from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import RoutePlanId
from backend.infrastructure.persistence.tables.clients import ClientAddress
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.persistence.tables.route_edge_history import (
    RouteEdgeHistory,
)
from backend.infrastructure.persistence.tables.route_plans import RoutePlan

BASE_URL = "/api/v1/route"

OPTIMIZER_COMPUTE = (
    "backend.application.services.tsp_solvers.route_optimizer"
    ".RouteOptimizer.compute"
)
OSRM_GET_GEOMETRY = (
    "backend.infrastructure.tsp_solvers.osrm.OSRMClient.get_route_geometry"
)


def _delivery_date_future() -> datetime:
    return datetime.now(UTC).date() + timedelta(days=1)


@pytest.mark.asyncio()
async def test_get_route_creates_route_plan(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    delivery_date = _delivery_date_future()
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Саксаганського",
            "house": "5",
            "coordinates": {"latitude": 50.44, "longitude": 30.51},
        },
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    with (
        patch(OPTIMIZER_COMPUTE, new_callable=AsyncMock, return_value=None),
        patch(OSRM_GET_GEOMETRY, new_callable=AsyncMock, return_value=None),
    ):
        response = await http_client.get(
            url=f"{BASE_URL}",
            headers=headers,
            params={"delivery_date": delivery_date.isoformat()},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["route_plan_id"] is not None
    assert len(data["points"]) == 2

    await session.flush()

    result = await session.execute(
        select(RoutePlan).where(RoutePlan.shop_id == shop_id)
    )
    route_plan = result.scalar_one()
    assert route_plan is not None
    assert route_plan.delivery_date == delivery_date


@pytest.mark.asyncio()
async def test_get_route_returns_existing_plan(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7001
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    delivery_date = _delivery_date_future()
    order_id_1 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_id_2 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Саксаганського",
            "house": "5",
            "coordinates": {"latitude": 50.44, "longitude": 30.51},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_id_2, order_id_1],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    with patch(OSRM_GET_GEOMETRY, new_callable=AsyncMock, return_value=None):
        response = await http_client.get(
            url=f"{BASE_URL}",
            headers=headers,
            params={"delivery_date": delivery_date.isoformat()},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["route_plan_id"] == str(route_plan_id)
    point_ids = [p["order_id"] for p in data["points"]]
    assert point_ids == [str(order_id_2), str(order_id_1)]


@pytest.mark.asyncio()
async def test_get_route_with_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7002
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    delivery_date = _delivery_date_future()

    order_in_slot = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_start_time=time(14, 0),
        delivery_end_time=time(21, 0),
        delivery_address={
            "street": "Саксаганського",
            "house": "5",
            "coordinates": {"latitude": 50.44, "longitude": 30.51},
        },
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    from sqlalchemy import select as sa_select

    from backend.infrastructure.persistence.tables.shops import (
        ShopDeliveryTimeSlot,
    )

    result = await session.execute(
        sa_select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.shop_id == shop_id,
            ShopDeliveryTimeSlot.start_time == time(9, 0),
            ShopDeliveryTimeSlot.end_time == time(14, 0),
        )
    )
    time_slot = result.scalar_one()

    with (
        patch(OPTIMIZER_COMPUTE, new_callable=AsyncMock, return_value=None),
        patch(OSRM_GET_GEOMETRY, new_callable=AsyncMock, return_value=None),
    ):
        response = await http_client.get(
            url=f"{BASE_URL}",
            headers=headers,
            params={
                "delivery_date": delivery_date.isoformat(),
                "time_slot_id": str(time_slot.id),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    point_ids = [p["order_id"] for p in data["points"]]
    assert str(order_in_slot) in point_ids
    assert len(data["points"]) == 1


@pytest.mark.asyncio()
async def test_reorder_route(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7003
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_a = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_b = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.54},
        },
    )
    order_c = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "C",
            "house": "3",
            "coordinates": {"latitude": 50.48, "longitude": 30.55},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_a, order_b, order_c],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}",
        headers=headers,
        json={
            "delivery_date": delivery_date.isoformat(),
            "order_id": str(order_c),
            "new_position": 0,
        },
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()

    result = await session.execute(
        select(RoutePlan).where(RoutePlan.id == route_plan_id)
    )
    route_plan = result.scalar_one()
    assert route_plan.order_sequence == [order_c, order_a, order_b]


@pytest.mark.asyncio()
async def test_reorder_route_plan_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7004
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}",
        headers=headers,
        json={
            "delivery_date": _delivery_date_future().isoformat(),
            "order_id": str(uuid.uuid4()),
            "new_position": 0,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_order_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7005
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={"street": "Хрещатик", "house": "10"},
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/orders/{order_id}/coordinates",
        headers=headers,
        json={"latitude": 50.46, "longitude": 30.53},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()
    session.expire_all()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.delivery_address.coordinates is not None
    assert order.delivery_address.coordinates.latitude == 50.46
    assert order.delivery_address.coordinates.longitude == 30.53


@pytest.mark.asyncio()
async def test_update_order_coordinates_propagates_to_client(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7006
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_id_1 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={"street": "Хрещатик", "house": "10"},
    )
    order_id_2 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={"street": "Хрещатик", "house": "10"},
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/orders/{order_id_1}/coordinates",
        headers=headers,
        json={"latitude": 50.46, "longitude": 30.53},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()
    session.expire_all()

    result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addr = result.scalar_one()
    assert addr.latitude == 50.46
    assert addr.longitude == 30.53

    result2 = await session.execute(
        select(Order).where(Order.id == order_id_2)
    )
    order2 = result2.scalar_one()
    assert order2.delivery_address.coordinates is not None
    assert order2.delivery_address.coordinates.latitude == 50.46
    assert order2.delivery_address.coordinates.longitude == 30.53


@pytest.mark.asyncio()
async def test_get_shared_route(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7007
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    delivery_date = _delivery_date_future()
    order_id_1 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_id_2 = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Саксаганського",
            "house": "5",
            "coordinates": {"latitude": 50.44, "longitude": 30.51},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_id_1, order_id_2],
        )
    )
    await session.commit()

    with patch(OSRM_GET_GEOMETRY, new_callable=AsyncMock, return_value=None):
        response = await http_client.get(
            url=f"{BASE_URL}/shared/{route_plan_id}",
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    point_ids = [p["order_id"] for p in data["points"]]
    assert str(order_id_1) in point_ids
    assert str(order_id_2) in point_ids


@pytest.mark.asyncio()
async def test_get_shared_route_not_found(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(
        url=f"{BASE_URL}/shared/{uuid.uuid4()}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_route_unroutable_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7008
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    delivery_date = _delivery_date_future()
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "Невідома",
            "house": "99",
        },
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    with (
        patch(OPTIMIZER_COMPUTE, new_callable=AsyncMock, return_value=None),
        patch(OSRM_GET_GEOMETRY, new_callable=AsyncMock, return_value=None),
    ):
        response = await http_client.get(
            url=f"{BASE_URL}",
            headers=headers,
            params={"delivery_date": delivery_date.isoformat()},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["points"]) == 1
    assert len(data["unroutable_orders"]) == 1


ORDERS_BASE_URL = "/api/v1/orders"


@pytest.mark.asyncio()
async def test_delete_order_removes_from_route_plan(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7009
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_a = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_b = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.54},
        },
    )
    order_c = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "C",
            "house": "3",
            "coordinates": {"latitude": 50.48, "longitude": 30.55},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_a, order_b, order_c],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{ORDERS_BASE_URL}/{order_b}", headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()
    session.expire_all()

    result = await session.execute(
        select(RoutePlan).where(RoutePlan.id == route_plan_id)
    )
    route_plan = result.scalar_one()
    assert order_b not in route_plan.order_sequence
    assert route_plan.order_sequence == [order_a, order_c]


@pytest.mark.asyncio()
async def test_update_coordinates_recalculates_route_position(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7010
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.0,
        shop_longitude=30.0,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_a = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "A",
            "house": "1",
            "coordinates": {"latitude": 50.1, "longitude": 30.1},
        },
    )
    order_b = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "B",
            "house": "2",
            "coordinates": {"latitude": 50.3, "longitude": 30.3},
        },
    )
    order_c = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "C",
            "house": "3",
            "coordinates": {"latitude": 50.5, "longitude": 30.5},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_a, order_b, order_c],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/orders/{order_a}/coordinates",
        headers=headers,
        json={"latitude": 50.5, "longitude": 30.5},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()
    session.expire_all()

    result = await session.execute(
        select(RoutePlan).where(RoutePlan.id == route_plan_id)
    )
    route_plan = result.scalar_one()
    assert order_a in route_plan.order_sequence
    assert len(route_plan.order_sequence) == 3
    assert route_plan.order_sequence.index(order_a) != 0


@pytest.mark.asyncio()
async def test_edit_order_date_change_removes_from_old_route_plan(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7011
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.46,
                "longitude": 30.53,
            }
        ],
    )

    old_date = _delivery_date_future()
    new_date = old_date + timedelta(days=1)

    order_a = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=old_date,
        delivery_address={
            "street": "A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_b = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=old_date,
        delivery_address={
            "street": "B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.54},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=old_date,
            time_slot_id=None,
            order_sequence=[order_a, order_b],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{ORDERS_BASE_URL}/{order_a}",
        headers=headers,
        json={"delivery_date": new_date.isoformat()},
    )
    assert response.status_code == status.HTTP_200_OK

    await session.flush()
    session.expire_all()

    result = await session.execute(
        select(RoutePlan).where(RoutePlan.id == route_plan_id)
    )
    route_plan = result.scalar_one()
    assert order_a not in route_plan.order_sequence
    assert route_plan.order_sequence == [order_b]


@pytest.mark.asyncio()
async def test_reorder_records_edge_history(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 7012
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.45,
        shop_longitude=30.52,
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )

    delivery_date = _delivery_date_future()
    order_a = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.53},
        },
    )
    order_b = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.54},
        },
    )
    order_c = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_address={
            "street": "C",
            "house": "3",
            "coordinates": {"latitude": 50.48, "longitude": 30.55},
        },
    )

    route_plan_id = RoutePlanId(uuid.uuid4())
    await session.execute(
        insert(RoutePlan).values(
            id=route_plan_id,
            shop_id=shop_id,
            delivery_date=delivery_date,
            time_slot_id=None,
            order_sequence=[order_a, order_b, order_c],
        )
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}",
        headers=headers,
        json={
            "delivery_date": delivery_date.isoformat(),
            "order_id": str(order_c),
            "new_position": 0,
        },
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()

    result = await session.execute(
        select(RouteEdgeHistory).where(RouteEdgeHistory.shop_id == shop_id)
    )
    edge_rows = result.scalars().all()
    assert len(edge_rows) >= 2
