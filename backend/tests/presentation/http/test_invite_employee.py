from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole

BASE_URL = "/api/v1/links"


@pytest.mark.parametrize("role", (ShopRole.MANAGER, ShopRole.COURIER))
@pytest.mark.asyncio()
async def test_create_invite_link_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    role: ShopRole,
) -> None:
    telegram_id = 1000
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    headers = customer_headers(telegram_id)
    full_name = "John Doe"

    json_data = {"role": role.value, "full_name": full_name}
    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    link = response.json()
    assert isinstance(link, str)
    assert link.startswith("https://t.me/")
    assert "start=" in link


@pytest.mark.asyncio()
async def test_create_invite_link_denied_for_manager(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2000
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json_data = {"role": ShopRole.COURIER.value, "full_name": "John Doe"}
    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_invite_link_denied_for_courier(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 3000
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json_data = {"role": ShopRole.MANAGER.value, "full_name": "John Doe"}
    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_invite_link_validation_error_for_owner_role(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json_data = {"role": ShopRole.OWNER.value, "full_name": "John Doe"}
    response = await http_client.post(
        url=BASE_URL, headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio()
async def test_create_invite_link_unauthorized_without_token(
    http_client: AsyncClient,
) -> None:
    json_data = {"role": ShopRole.MANAGER.value, "full_name": "John Doe"}
    response = await http_client.post(url=BASE_URL, json=json_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
