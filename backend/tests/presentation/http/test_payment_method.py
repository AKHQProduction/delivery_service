import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole
from backend.infrastructure.persistence.tables.shops import (
    ShopPaymentMethod,
)

BASE_URL = "/api/v1/payment-methods"


@pytest.mark.asyncio()
async def test_create_payment_method(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.post(
        url=BASE_URL,
        headers=headers,
        json={"name": "Картка"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    payment_method_id = response.json()
    assert payment_method_id is not None

    await session.flush()

    result = await session.execute(
        select(ShopPaymentMethod).where(
            ShopPaymentMethod.id == uuid.UUID(payment_method_id)
        )
    )
    pm = result.scalar_one()
    assert pm.shop_id == shop_id
    assert pm.name == "Картка"


@pytest.mark.asyncio()
async def test_create_payment_method_duplicate_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8001
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.post(
        url=BASE_URL,
        headers=headers,
        json={"name": "Готівка"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_create_payment_method_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8002
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.post(
        url=BASE_URL,
        headers=headers,
        json={"name": "Картка"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_payment_method_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.post(url=BASE_URL, json={"name": "Картка"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_update_payment_method(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_payment_method,
) -> None:
    telegram_id = 8100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    pm_id = await setup_test_payment_method(
        shop_id=shop_id, name="Старий метод"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{pm_id}",
        headers=headers,
        json={"name": "Новий метод"},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(ShopPaymentMethod).where(ShopPaymentMethod.id == pm_id)
    )
    pm = result.scalar_one()
    assert pm.name == "Новий метод"


@pytest.mark.asyncio()
async def test_update_payment_method_duplicate_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_payment_method,
) -> None:
    telegram_id = 8101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    pm_id = await setup_test_payment_method(shop_id=shop_id, name="Метод A")
    await setup_test_payment_method(shop_id=shop_id, name="Метод B")
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{pm_id}",
        headers=headers,
        json={"name": "Метод B"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_update_payment_method_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8102
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"name": "Новий метод"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_payment_method_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_payment_method,
) -> None:
    telegram_id = 8103
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    pm_id = await setup_test_payment_method(shop_id=shop_id, name="Тест")
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{pm_id}",
        headers=headers,
        json={"name": "Новий"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_payment_method_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}", json={"name": "Тест"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_delete_payment_method(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_payment_method,
) -> None:
    telegram_id = 8200
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    pm_id = await setup_test_payment_method(
        shop_id=shop_id, name="Для видалення"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{pm_id}", headers=headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()

    result = await session.execute(
        select(ShopPaymentMethod).where(ShopPaymentMethod.id == pm_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_delete_last_payment_method_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    create_user,
    create_telegram_account,
    create_shop,
    create_role,
    create_shop_membership,
    setup_test_payment_method,
) -> None:
    telegram_id = 8201
    user_id = await create_user()
    await create_telegram_account(
        user_id=user_id, telegram_id=telegram_id, full_name="Test User"
    )
    role_id = await create_role(name=ShopRole.OWNER)
    shop_id = await create_shop()
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id
    )
    pm_id = await setup_test_payment_method(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{pm_id}", headers=headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "last payment method" in response.json()["detail"]


@pytest.mark.asyncio()
async def test_delete_payment_method_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8202
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{uuid.uuid4()}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_payment_method_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_payment_method,
) -> None:
    telegram_id = 8203
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    pm_id = await setup_test_payment_method(shop_id=shop_id, name="Тест")
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{pm_id}", headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_payment_method_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.delete(url=f"{BASE_URL}/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_get_all_payment_methods(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 8300
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(url=f"{BASE_URL}/all", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    methods = response.json()
    assert len(methods) == 3
    names = [m["name"] for m in methods]
    assert "Готівка" in names
    assert "На рахунок" in names
    assert "Інше" in names


@pytest.mark.asyncio()
async def test_get_all_payment_methods_filters_by_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_test_payment_method,
    create_user,
    create_telegram_account,
    create_role,
    create_shop_membership,
    create_shop,
) -> None:
    user1_telegram_id = 8301
    user2_telegram_id = 8302

    role_id = await create_role(role_id=1, name=ShopRole.OWNER)

    shop_id_1 = await create_shop()
    user_id_1 = await create_user()
    await create_telegram_account(
        user_id=user_id_1,
        telegram_id=user1_telegram_id,
        full_name="User 1",
    )
    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id_1, role_id=role_id
    )

    shop_id_2 = await create_shop()
    user_id_2 = await create_user()
    await create_telegram_account(
        user_id=user_id_2,
        telegram_id=user2_telegram_id,
        full_name="User 2",
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id_2, role_id=role_id
    )

    await setup_test_payment_method(shop_id=shop_id_1, name="Готівка")
    await setup_test_payment_method(shop_id=shop_id_1, name="Картка")
    await setup_test_payment_method(shop_id=shop_id_2, name="Готівка")

    await session.commit()

    headers_1 = customer_headers(user1_telegram_id)
    headers_2 = customer_headers(user2_telegram_id)

    response_1 = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers_1
    )
    response_2 = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers_2
    )

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK

    assert len(response_1.json()) == 2
    assert len(response_2.json()) == 1


@pytest.mark.asyncio()
async def test_get_all_payment_methods_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/all")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
