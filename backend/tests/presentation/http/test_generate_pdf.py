from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_URL = "/api/v1/orders/export/pdf"


@pytest.fixture()
def tomorrow() -> date:
    return datetime.now(UTC).date() + timedelta(days=1)


@pytest.mark.asyncio()
async def test_generate_pdf_returns_file_id_and_filename(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    await setup_test_order(
        shop_id=shop_id, client_id=client_id, delivery_date=tomorrow
    )
    await session.commit()

    response = await http_client.post(
        url=f"{BASE_URL}/generate",
        json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
        headers=customer_headers(telegram_id),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "file_id" in data
    assert "filename" in data
    assert data["filename"] == f"orders_{tomorrow.isoformat()}.pdf"


@pytest.mark.asyncio()
async def test_generate_pdf_and_download(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5001
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    await setup_test_order(
        shop_id=shop_id, client_id=client_id, delivery_date=tomorrow
    )
    await session.commit()

    gen_response = await http_client.post(
        url=f"{BASE_URL}/generate",
        json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
        headers=customer_headers(telegram_id),
    )
    assert gen_response.status_code == status.HTTP_200_OK
    file_id = gen_response.json()["file_id"]

    dl_response = await http_client.get(url=f"{BASE_URL}/download/{file_id}")

    assert dl_response.status_code == status.HTTP_200_OK
    assert dl_response.headers["content-type"] == "application/pdf"
    assert b"%PDF" in dl_response.content


@pytest.mark.asyncio()
async def test_generate_pdf_no_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    tomorrow,
) -> None:
    telegram_id = 5002
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    response = await http_client.post(
        url=f"{BASE_URL}/generate",
        json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
        headers=customer_headers(telegram_id),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "file_id" in data


@pytest.mark.asyncio()
async def test_generate_pdf_unauthorized(
    http_client: AsyncClient,
    tomorrow,
) -> None:
    response = await http_client.post(
        url=f"{BASE_URL}/generate",
        json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_download_pdf_not_found(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/download/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_generate_pdf_multiple_time_slots(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5003
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(14, 0),
        delivery_end_time=time(21, 0),
    )
    await session.commit()

    response = await http_client.post(
        url=f"{BASE_URL}/generate",
        json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
        headers=customer_headers(telegram_id),
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
async def test_generate_pdf_with_coordinates_triggers_optimization(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5004
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.4501,
        shop_longitude=30.5234,
    )

    client_id = await setup_test_client(shop_id=shop_id)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.52},
        },
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.53},
        },
    )
    await session.commit()

    with patch(
        "backend.application.services.tsp_solvers.route_optimizer.RouteOptimizer.compute",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_compute:
        response = await http_client.post(
            url=f"{BASE_URL}/generate",
            json={
                "delivery_date": str(tomorrow),
                "doc_type": "ORDER_LIST",
                "routing_mode": "OPTIMIZED",
            },
            headers=customer_headers(telegram_id),
        )

        assert response.status_code == status.HTTP_200_OK
        mock_compute.assert_called_once()


@pytest.mark.asyncio()
async def test_generate_pdf_without_shop_coordinates_skips_optimization(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5005
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.52},
        },
    )
    await session.commit()

    with patch(
        "backend.application.services.tsp_solvers.route_optimizer.RouteOptimizer.compute",
        new_callable=AsyncMock,
    ) as mock_compute:
        response = await http_client.post(
            url=f"{BASE_URL}/generate",
            json={
                "delivery_date": str(tomorrow),
                "doc_type": "ORDER_LIST",
                "routing_mode": "OPTIMIZED",
            },
            headers=customer_headers(telegram_id),
        )

        assert response.status_code == status.HTTP_200_OK
        mock_compute.assert_not_called()


@pytest.mark.asyncio()
async def test_generate_pdf_default_routing_skips_optimization(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5006
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.4501,
        shop_longitude=30.5234,
    )

    client_id = await setup_test_client(shop_id=shop_id)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.52},
        },
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.53},
        },
    )
    await session.commit()

    with patch(
        "backend.application.services.tsp_solvers.route_optimizer.RouteOptimizer.compute",
        new_callable=AsyncMock,
    ) as mock_compute:
        response = await http_client.post(
            url=f"{BASE_URL}/generate",
            json={"delivery_date": str(tomorrow), "doc_type": "ORDER_LIST"},
            headers=customer_headers(telegram_id),
        )

        assert response.status_code == status.HTTP_200_OK
        mock_compute.assert_not_called()


@pytest.mark.asyncio()
async def test_generate_pdf_optimized_routing(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    tomorrow,
) -> None:
    telegram_id = 5007
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        shop_latitude=50.4501,
        shop_longitude=30.5234,
    )

    client_id = await setup_test_client(shop_id=shop_id)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street A",
            "house": "1",
            "coordinates": {"latitude": 50.46, "longitude": 30.52},
        },
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_address={
            "street": "Street B",
            "house": "2",
            "coordinates": {"latitude": 50.47, "longitude": 30.53},
        },
    )
    await session.commit()

    with patch(
        "backend.application.services.tsp_solvers.route_optimizer.RouteOptimizer.compute",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_compute:
        response = await http_client.post(
            url=f"{BASE_URL}/generate",
            json={
                "delivery_date": str(tomorrow),
                "doc_type": "ORDER_LIST",
                "routing_mode": "OPTIMIZED",
            },
            headers=customer_headers(telegram_id),
        )

        assert response.status_code == status.HTTP_200_OK
        mock_compute.assert_called_once()
