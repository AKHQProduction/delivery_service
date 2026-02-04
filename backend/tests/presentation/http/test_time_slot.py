import uuid
from collections.abc import Callable
from datetime import time
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)

BASE_URL = "/api/v1/time-slots"


@pytest.mark.asyncio()
async def test_create_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "06:00:00",
        "end_time": "09:00:00",
        "label": "Ранкова доставка",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    time_slot_id = response.json()
    assert time_slot_id is not None

    await session.flush()

    result = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.id == uuid.UUID(time_slot_id)
        )
    )
    time_slot = result.scalar_one()
    assert time_slot.shop_id == shop_id
    assert time_slot.start_time == time(6, 0)
    assert time_slot.end_time == time(9, 0)
    assert time_slot.label == "Ранкова доставка"


@pytest.mark.asyncio()
async def test_create_time_slot_without_label(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7001
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "14:00:00",
        "end_time": "20:00:00",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    time_slot_id = response.json()

    await session.flush()

    result = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.id == uuid.UUID(time_slot_id)
        )
    )
    time_slot = result.scalar_one()
    assert time_slot.label is None


@pytest.mark.asyncio()
async def test_create_time_slot_duplicate_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7002
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "09:00:00",
        "end_time": "14:00:00",
        "label": "Duplicate slot",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_create_time_slot_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7003
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "09:00:00",
        "end_time": "14:00:00",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_time_slot_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {
        "start_time": "09:00:00",
        "end_time": "14:00:00",
    }

    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(6, 0),
        end_time=time(9, 0),
        label="Original label",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "07:00:00",
        "end_time": "10:00:00",
        "label": "Updated label",
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.id == time_slot_id
        )
    )
    time_slot = result.scalar_one()
    assert time_slot.start_time == time(7, 0)
    assert time_slot.end_time == time(10, 0)
    assert time_slot.label == "Updated label"


@pytest.mark.asyncio()
async def test_update_time_slot_partial(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(6, 0),
        end_time=time(9, 0),
        label="Original label",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "label": "Only label updated",
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.id == time_slot_id
        )
    )
    time_slot = result.scalar_one()
    assert time_slot.start_time == time(6, 0)
    assert time_slot.end_time == time(9, 0)
    assert time_slot.label == "Only label updated"


@pytest.mark.asyncio()
async def test_update_time_slot_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7102
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "label": "New label",
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7200
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id, start_time=time(6, 0), end_time=time(9, 0)
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()

    result = await session.execute(
        select(ShopDeliveryTimeSlot).where(
            ShopDeliveryTimeSlot.id == time_slot_id
        )
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_delete_last_time_slot_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    create_user,
    create_telegram_account,
    create_shop,
    create_role,
    create_shop_membership,
    setup_test_time_slot,
) -> None:
    telegram_id = 7202
    user_id = await create_user()
    await create_telegram_account(
        user_id=user_id, telegram_id=telegram_id, full_name="Test User"
    )
    role_id = await create_role(name=ShopRole.OWNER)
    shop_id = await create_shop()
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id
    )
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "last time slot" in response.json()["detail"]


@pytest.mark.asyncio()
async def test_delete_time_slot_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7201
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{uuid.uuid4()}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_all_time_slots(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 7300
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(url=f"{BASE_URL}/all", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    time_slots = response.json()
    assert len(time_slots) == 2
    assert time_slots[0]["start_time"] == "09:00"
    assert time_slots[1]["start_time"] == "14:00"


@pytest.mark.asyncio()
async def test_get_all_time_slots_filters_by_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_test_time_slot,
    create_user,
    create_telegram_account,
    create_role,
    create_shop_membership,
    create_shop,
) -> None:
    user1_telegram_id = 7301
    user2_telegram_id = 7302

    role_id = await create_role(role_id=1, name=ShopRole.OWNER)

    shop_id_1 = await create_shop()
    user_id_1 = await create_user()
    await create_telegram_account(
        user_id=user_id_1, telegram_id=user1_telegram_id, full_name="User 1"
    )
    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id_1, role_id=role_id
    )

    shop_id_2 = await create_shop()
    user_id_2 = await create_user()
    await create_telegram_account(
        user_id=user_id_2, telegram_id=user2_telegram_id, full_name="User 2"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id_2, role_id=role_id
    )

    await setup_test_time_slot(shop_id=shop_id_1)
    await setup_test_time_slot(
        shop_id=shop_id_1, start_time=time(14, 0), end_time=time(20, 0)
    )
    await setup_test_time_slot(shop_id=shop_id_2)

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
async def test_update_time_slot_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7103
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id, start_time=time(6, 0), end_time=time(9, 0)
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"label": "New label"}
    response = await http_client.patch(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_time_slot_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"label": "New label"}
    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}", json=json
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_time_slot_duplicate_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7104
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(6, 0),
        end_time=time(9, 0),
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "start_time": "09:00:00",
        "end_time": "14:00:00",
    }
    response = await http_client.patch(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_delete_time_slot_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 7203
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id, start_time=time(6, 0), end_time=time(9, 0)
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{time_slot_id}", headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_time_slot_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.delete(url=f"{BASE_URL}/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_all_time_slots_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/all")

    assert response.status_code == status.HTTP_403_FORBIDDEN
