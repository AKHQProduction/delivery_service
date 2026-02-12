from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole

BASE_URL = "/api/v1/users"


@pytest.mark.parametrize(
    ("telegram_id", "role"),
    (
        (1000, ShopRole.OWNER),
        (2000, ShopRole.MANAGER),
        (3000, ShopRole.COURIER),
    ),
)
@pytest.mark.asyncio()
async def test_me_return_correct_id_and_role(
    http_client: AsyncClient,
    telegram_id: int,
    role: ShopRole,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    user_id, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=role
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + "/me"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "user": {
            "user_id": str(user_id),
            "full_name": "Test User",
            "role": role.value,
        },
        "shop": {
            "shop_id": str(shop_id),
            "city": None,
            "street": None,
            "house": None,
        },
    }


@pytest.mark.asyncio()
async def test_me_returns_shop_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 4000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id,
        role=ShopRole.OWNER,
        shop_city="Київ",
        shop_street="Хрещатик",
        shop_house="1",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + "/me"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["shop"] == {
        "shop_id": str(shop_id),
        "city": "Київ",
        "street": "Хрещатик",
        "house": "1",
    }


@pytest.mark.asyncio()
async def test_me_unauthorized(
    http_client: AsyncClient,
) -> None:
    url = BASE_URL + "/me"
    response = await http_client.get(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
