from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole
from backend.infrastructure.persistence.tables.shops import (
    Shop,
    ShopDeliveryTimeSlot,
    ShopMembership,
)

BASE_URL = "/api/v1/shop"


@pytest.mark.asyncio()
async def test_create_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    create_user,
    create_telegram_account,
    create_role,
) -> None:
    telegram_id = 9100
    user_id = await create_user()
    await create_telegram_account(user_id=user_id, telegram_id=telegram_id)
    await create_role(name=ShopRole.OWNER)
    await session.flush()

    headers = customer_headers(telegram_id)
    json_data = {"name": "Моя крамниця", "owner_full_name": "Іван Іванов"}

    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_201_CREATED

    await session.flush()

    result = await session.execute(select(Shop))
    shop = result.scalar_one()
    assert shop.name == "Моя крамниця"

    memberships = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    membership = memberships.scalar_one()
    assert membership.shop_id == shop.id
    assert membership.name == "Іван Іванов"

    time_slots = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.shop_id == shop.id
        )
    )
    assert len(time_slots.fetchall()) == 2


@pytest.mark.asyncio()
async def test_create_shop_user_already_has_shop_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 9101
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.flush()

    headers = customer_headers(telegram_id)
    json_data = {"name": "Друга крамниця", "owner_full_name": "Петро Петров"}

    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_create_shop_unauthorized(
    http_client: AsyncClient,
) -> None:
    json_data = {"name": "Крамниця", "owner_full_name": "Іван Іванов"}

    response = await http_client.post(url=BASE_URL, json=json_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
            "city": "Київ",
            "street": "Хрещатик",
            "house": "1",
            "coordinates": {
                "latitude": 50.4501,
                "longitude": 30.5234,
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
    assert shop.city == "Київ"
    assert shop.street == "Хрещатик"
    assert shop.house == "1"
    assert shop.latitude == pytest.approx(50.4501)
    assert shop.longitude == pytest.approx(30.5234)


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
            "city": "Київ",
            "street": "Хрещатик",
            "house": "1",
            "coordinates": {
                "latitude": 50.4501,
                "longitude": 30.5234,
            },
        }
    }
    await http_client.patch(url=BASE_URL, headers=headers, json=first_address)

    second_address = {
        "address": {
            "city": "Одеса",
            "street": "Дерибасівська",
            "house": "5",
            "coordinates": {
                "latitude": 46.4825,
                "longitude": 30.7233,
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
    assert shop.city == "Одеса"
    assert shop.street == "Дерибасівська"
    assert shop.house == "5"


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
            "city": "Київ",
            "street": "Хрещатик",
            "house": "1",
            "coordinates": {
                "latitude": 50.4501,
                "longitude": 30.5234,
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
            "city": "Київ",
            "street": "Хрещатик",
            "house": "1",
            "coordinates": {
                "latitude": 50.4501,
                "longitude": 30.5234,
            },
        }
    }

    response = await http_client.patch(url=BASE_URL, json=json_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
