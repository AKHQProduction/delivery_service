import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import (
    RecurringOrderStatus,
    ScheduleType,
)
from backend.infrastructure.persistence.tables.clients import (
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)

BASE_URL = "/api/v1/recurring-orders"


async def _client_refs(
    session: AsyncSession, client_id: uuid.UUID
) -> tuple[int, int]:
    phone_result = await session.execute(
        select(ClientPhone.id).where(ClientPhone.client_id == client_id)
    )
    address_result = await session.execute(
        select(ClientAddress.id).where(ClientAddress.client_id == client_id)
    )
    return phone_result.scalar_one(), address_result.scalar_one()


async def _time_slot_id(
    session: AsyncSession, shop_id: uuid.UUID
) -> uuid.UUID:
    result = await session.execute(
        select(ShopDeliveryTimeSlot.id).where(
            ShopDeliveryTimeSlot.shop_id == shop_id
        )
    )
    return result.scalars().first()


@pytest.mark.asyncio()
async def test_create_weekly_recurring_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json={
            "client_id": str(client_id),
            "address_id": address_id,
            "phone_id": phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 2}],
            "payment_method": "Баланс",
            "comment": "Залишити біля дверей",
            "schedule_type": "WEEKLY",
            "weekdays": [5, 1, 3],
            "month_days": None,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    recurring_order_id = uuid.UUID(response.json())

    result = await session.execute(
        select(RecurringOrder).where(RecurringOrder.id == recurring_order_id)
    )
    recurring_order = result.scalar_one()
    assert recurring_order.shop_id == shop_id
    assert recurring_order.client_id == client_id
    assert recurring_order.address_id == address_id
    assert recurring_order.phone_id == phone_id
    assert recurring_order.time_slot_id == time_slot_id
    assert recurring_order.status == RecurringOrderStatus.ACTIVE
    assert recurring_order.schedule_type == ScheduleType.WEEKLY
    assert recurring_order.weekdays == [1, 3, 5]
    assert recurring_order.month_days is None
    assert recurring_order.payment_method == "Баланс"
    assert recurring_order.comment == "Залишити біля дверей"

    item_result = await session.execute(
        select(RecurringOrderItem).where(
            RecurringOrderItem.recurring_order_id == recurring_order_id
        )
    )
    item = item_result.scalar_one()
    assert item.product_id == product_id
    assert item.quantity == 2


@pytest.mark.asyncio()
async def test_get_recurring_orders_list_and_detail(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Олена Коваль",
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, product_name, product_price, _ = await setup_test_product(
        shop_id=shop_id
    )
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    create_response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json={
            "client_id": str(client_id),
            "address_id": address_id,
            "phone_id": phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 1}],
            "payment_method": "Готівка",
            "comment": None,
            "schedule_type": "MONTHLY_BY_DAY",
            "weekdays": None,
            "month_days": [20, 5],
        },
    )
    recurring_order_id = create_response.json()

    list_response = await http_client.get(
        BASE_URL,
        headers=customer_headers(telegram_id),
        params={"client_name": "Олена", "month_day": 5},
    )

    assert list_response.status_code == status.HTTP_200_OK
    payload = list_response.json()
    assert len(payload) == 1
    row = payload[0]
    assert row["recurring_order_id"] == recurring_order_id
    assert row["client_name"] == "Олена Коваль"
    assert row["phone_number"] == "+380501111111"
    assert row["address_summary"] == "Хрещатик, 10"
    assert row["schedule_type"] == "MONTHLY_BY_DAY"
    assert row["month_days"] == [5, 20]
    assert row["time_slot_id"] == str(time_slot_id)
    assert row["items_count"] == 1
    assert row["status"] == "ACTIVE"

    detail_response = await http_client.get(
        f"{BASE_URL}/{recurring_order_id}",
        headers=customer_headers(telegram_id),
    )

    assert detail_response.status_code == status.HTTP_200_OK
    detail = detail_response.json()
    assert detail["recurring_order_id"] == recurring_order_id
    assert detail["items"] == [
        {
            "product_id": str(product_id),
            "product_name": product_name,
            "quantity": 1,
            "current_price": product_price,
        }
    ]


@pytest.mark.asyncio()
async def test_pause_resume_and_delete_recurring_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9102
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    create_response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json={
            "client_id": str(client_id),
            "address_id": address_id,
            "phone_id": phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 1}],
            "payment_method": "Готівка",
            "comment": None,
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = create_response.json()

    pause_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/pause",
        headers=customer_headers(telegram_id),
    )
    assert pause_response.status_code == status.HTTP_200_OK

    row = await session.get(RecurringOrder, uuid.UUID(recurring_order_id))
    assert row is not None
    assert row.status == RecurringOrderStatus.PAUSED

    resume_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/resume",
        headers=customer_headers(telegram_id),
    )
    assert resume_response.status_code == status.HTTP_200_OK
    assert row.status == RecurringOrderStatus.ACTIVE

    delete_response = await http_client.delete(
        f"{BASE_URL}/{recurring_order_id}",
        headers=customer_headers(telegram_id),
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        await session.get(RecurringOrder, uuid.UUID(recurring_order_id))
        is None
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "payload_patch",
    (
        {"weekdays": []},
        {"weekdays": [1, 1]},
        {"weekdays": [0]},
        {"items": []},
        {"items": [{"product_id": str(uuid.uuid4()), "quantity": 0}]},
    ),
)
async def test_create_recurring_order_validation_errors(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    payload_patch: dict[str, Any],
) -> None:
    telegram_id = 9103
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    payload: dict[str, Any] = {
        "client_id": str(client_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "time_slot_id": str(time_slot_id),
        "items": [{"product_id": str(product_id), "quantity": 1}],
        "payment_method": "Готівка",
        "comment": None,
        "schedule_type": "WEEKLY",
        "weekdays": [1],
        "month_days": None,
    }
    payload.update(payload_patch)

    response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio()
async def test_edit_client_repoints_recurring_order_refs_when_ids_change(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9104
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Марія",
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    old_phone_id, old_address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    create_response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json={
            "client_id": str(client_id),
            "address_id": old_address_id,
            "phone_id": old_phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 1}],
            "payment_method": "Готівка",
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = create_response.json()

    response = await http_client.patch(
        f"/api/v1/clients/{client_id}",
        headers=customer_headers(telegram_id),
        json={
            "phones": [
                {"number": "+380501111111", "is_primary": True},
            ],
            "addresses": [
                {
                    "street": "Хрещатик",
                    "house": "10",
                    "is_primary": True,
                },
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    new_phone_id, new_address_id = await _client_refs(session, client_id)
    recurring_order = await session.get(
        RecurringOrder, uuid.UUID(recurring_order_id)
    )
    assert recurring_order is not None
    assert recurring_order.phone_id == new_phone_id
    assert recurring_order.phone_id != old_phone_id
    assert recurring_order.address_id == new_address_id
    assert recurring_order.address_id != old_address_id
    assert recurring_order.status == RecurringOrderStatus.ACTIVE


@pytest.mark.asyncio()
async def test_edit_client_pauses_recurring_order_when_refs_removed(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9105
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Іван",
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    old_phone_id, old_address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    create_response = await http_client.post(
        BASE_URL,
        headers=customer_headers(telegram_id),
        json={
            "client_id": str(client_id),
            "address_id": old_address_id,
            "phone_id": old_phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 1}],
            "payment_method": "Готівка",
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = create_response.json()

    response = await http_client.patch(
        f"/api/v1/clients/{client_id}",
        headers=customer_headers(telegram_id),
        json={"phones": [], "addresses": []},
    )

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    recurring_order = await session.get(
        RecurringOrder, uuid.UUID(recurring_order_id)
    )
    assert recurring_order is not None
    assert recurring_order.phone_id is None
    assert recurring_order.address_id is None
    assert recurring_order.status == RecurringOrderStatus.PAUSED
