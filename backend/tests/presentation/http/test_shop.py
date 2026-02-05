from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole
from backend.infrastructure.persistence.tables.shops import Shop

BASE_URL = "/api/v1/shop"


@pytest.mark.asyncio()
async def test_update_shop_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 9000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json_data = {
        "address": {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "coordinates": {
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
        }
    }

    response = await http_client.patch(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one()
    assert shop.city == "Moscow"
    assert shop.street == "Lenina"
    assert shop.house == "10"
    assert shop.latitude == pytest.approx(55.7558)
    assert shop.longitude == pytest.approx(37.6173)


@pytest.mark.asyncio()
async def test_update_shop_address_overwrites_previous(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 9001
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    first_address = {
        "address": {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "coordinates": {
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
        }
    }
    await http_client.patch(url=BASE_URL, headers=headers, json=first_address)

    second_address = {
        "address": {
            "city": "SPb",
            "street": "Nevsky",
            "house": "1",
            "coordinates": {
                "latitude": 59.9343,
                "longitude": 30.3351,
            },
        }
    }
    response = await http_client.patch(
        url=BASE_URL, headers=headers, json=second_address
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one()
    assert shop.city == "SPb"
    assert shop.street == "Nevsky"
    assert shop.house == "1"


@pytest.mark.asyncio()
async def test_update_shop_without_address_noop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 9002
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(url=BASE_URL, headers=headers, json={})

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one()
    assert shop.city is None
    assert shop.street is None
    assert shop.house is None
    assert shop.latitude is None
    assert shop.longitude is None


@pytest.mark.asyncio()
async def test_update_shop_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 9003
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json_data = {
        "address": {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "coordinates": {
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
        }
    }

    response = await http_client.patch(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_shop_unauthorized(
    http_client: AsyncClient,
) -> None:
    json_data = {
        "address": {
            "city": "Moscow",
            "street": "Lenina",
            "house": "10",
            "coordinates": {
                "latitude": 55.7558,
                "longitude": 37.6173,
            },
        }
    }

    response = await http_client.patch(url=BASE_URL, json=json_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
