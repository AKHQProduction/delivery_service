import uuid
from collections.abc import Callable
from datetime import date
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import (
    RecurringOrderOccurrenceStatus,
    RecurringOrderStatus,
    ScheduleType,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.orders import Order, OrderItem
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
    RecurringOrderOccurrence,
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
    time_slot_id = result.scalars().first()
    assert time_slot_id is not None
    return time_slot_id


async def _create_recurring_order(
    http_client: AsyncClient,
    headers: dict[str, Any],
    *,
    client_id: uuid.UUID,
    address_id: int,
    phone_id: int,
    time_slot_id: uuid.UUID,
    product_id: uuid.UUID,
    weekdays: list[int],
    payment_method: str = "Готівка",
) -> uuid.UUID:
    response = await http_client.post(
        BASE_URL,
        headers=headers,
        json={
            "client_id": str(client_id),
            "address_id": address_id,
            "phone_id": phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [{"product_id": str(product_id), "quantity": 1}],
            "payment_method": payment_method,
            "schedule_type": "WEEKLY",
            "weekdays": weekdays,
            "month_days": None,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return uuid.UUID(response.json())


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
    await session.flush()
    session.expire_all()
    assert (
        await session.get(RecurringOrder, uuid.UUID(recurring_order_id))
        is None
    )


@pytest.mark.asyncio()
async def test_update_recurring_order_template(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 91022
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    second_product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()

    recurring_order_id = await _create_recurring_order(
        http_client,
        customer_headers(telegram_id),
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[1],
    )

    response = await http_client.patch(
        f"{BASE_URL}/{recurring_order_id}",
        headers=customer_headers(telegram_id),
        json={
            "address_id": address_id,
            "phone_id": phone_id,
            "time_slot_id": str(time_slot_id),
            "items": [
                {"product_id": str(product_id), "quantity": 2},
                {"product_id": str(second_product_id), "quantity": 1},
            ],
            "payment_method": "Баланс",
            "comment": "Оновлений шаблон",
            "schedule_type": "MONTHLY_BY_DAY",
            "weekdays": None,
            "month_days": [13, 5],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await session.flush()
    session.expire_all()

    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    assert recurring_order.schedule_type == ScheduleType.MONTHLY_BY_DAY
    assert recurring_order.weekdays is None
    assert recurring_order.month_days == [5, 13]
    assert recurring_order.payment_method == "Баланс"
    assert recurring_order.comment == "Оновлений шаблон"

    item_result = await session.execute(
        select(RecurringOrderItem)
        .where(RecurringOrderItem.recurring_order_id == recurring_order_id)
        .order_by(RecurringOrderItem.quantity.desc())
    )
    items = item_result.scalars().all()
    assert [(item.product_id, item.quantity) for item in items] == [
        (product_id, 2),
        (second_product_id, 1),
    ]


@pytest.mark.asyncio()
async def test_resume_recurring_order_rejects_invalid_template(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 91021
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
    recurring_order_id = uuid.UUID(create_response.json())

    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    recurring_order.status = RecurringOrderStatus.PAUSED
    recurring_order.time_slot_id = None
    await session.flush()

    resume_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/resume",
        headers=customer_headers(telegram_id),
    )

    assert resume_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resume_response.json()["detail"] == (
        "Recurring order template is invalid"
    )
    assert recurring_order.status == RecurringOrderStatus.PAUSED


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


@pytest.mark.asyncio()
async def test_run_recurring_order_creates_scheduled_orders_for_default_window(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9106
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "24",
                "comment": "Під'їзд з двору",
            }
        ],
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
            "items": [{"product_id": str(product_id), "quantity": 2}],
            "payment_method": "Готівка",
            "comment": "Залишити біля дверей",
            "schedule_type": "WEEKLY",
            "weekdays": [1, 3, 5],
            "month_days": None,
        },
    )
    recurring_order_id = create_response.json()

    response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["created_dates"] == [
        "2026-05-11",
        "2026-05-13",
        "2026-05-15",
        "2026-05-18",
        "2026-05-20",
        "2026-05-22",
    ]
    assert payload["already_scheduled_dates"] == []
    assert payload["cancelled_dates"] == []
    assert payload["paused"] is False
    await session.flush()

    rows = (
        (
            await session.execute(
                select(RecurringOrderOccurrence)
                .where(
                    RecurringOrderOccurrence.recurring_order_id
                    == uuid.UUID(recurring_order_id)
                )
                .order_by(RecurringOrderOccurrence.scheduled_for)
            )
        )
        .scalars()
        .all()
    )
    assert [row.scheduled_for for row in rows] == [
        date(2026, 5, 11),
        date(2026, 5, 13),
        date(2026, 5, 15),
        date(2026, 5, 18),
        date(2026, 5, 20),
        date(2026, 5, 22),
    ]
    assert {row.status for row in rows} == {
        RecurringOrderOccurrenceStatus.SCHEDULED
    }
    assert all(row.order_id for row in rows)

    first_order_id = rows[0].order_id
    assert first_order_id is not None
    first_order = (
        await session.execute(select(Order).where(Order.id == first_order_id))
    ).scalar_one()
    assert first_order.recurring_order_id == uuid.UUID(recurring_order_id)
    assert first_order.time_slot_id == time_slot_id
    assert first_order.date == date(2026, 5, 11)
    assert first_order.delivery_start_time.isoformat() == "09:00:00"
    assert first_order.delivery_end_time.isoformat() == "14:00:00"
    assert first_order.delivery_phone == "+380501111111"
    assert first_order.delivery_address.street == "Хрещатик"
    assert first_order.delivery_address.house == "10"
    assert first_order.delivery_address.apartment == "24"
    assert first_order.delivery_address.comment == "Під'їзд з двору"
    assert first_order.payment_method == "Готівка"
    assert first_order.comment == "Залишити біля дверей"

    first_item = (
        await session.execute(
            select(OrderItem).where(OrderItem.order_id == first_order_id)
        )
    ).scalar_one()
    assert first_item.product_id == product_id
    assert first_item.name == product_name
    assert first_item.price_per_item == product_price
    assert first_item.quantity == 2

    rerun_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )
    assert rerun_response.status_code == status.HTTP_200_OK
    rerun_payload = rerun_response.json()
    assert rerun_payload["created_dates"] == []
    assert rerun_payload["already_scheduled_dates"] == [
        "2026-05-11",
        "2026-05-13",
        "2026-05-15",
        "2026-05-18",
        "2026-05-20",
        "2026-05-22",
    ]
    await session.flush()

    order_count = (
        (
            await session.execute(
                select(Order).where(
                    Order.recurring_order_id == uuid.UUID(recurring_order_id)
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(order_count) == 6


@pytest.mark.asyncio()
async def test_run_paused_recurring_order_requires_activation(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9107
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

    blocked_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )

    assert blocked_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert blocked_response.json()["detail"] == "Recurring order is paused"

    activated_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False, "activate": True},
    )
    assert activated_response.status_code == status.HTTP_200_OK
    assert activated_response.json()["created_dates"] == [
        "2026-05-11",
        "2026-05-18",
    ]

    recurring_order = await session.get(
        RecurringOrder, uuid.UUID(recurring_order_id)
    )
    assert recurring_order is not None
    assert recurring_order.status == RecurringOrderStatus.ACTIVE


@pytest.mark.asyncio()
async def test_run_recurring_order_skips_cancelled_occurrences(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9108
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
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = uuid.UUID(create_response.json())
    session.add(
        RecurringOrderOccurrence(
            recurring_order_id=recurring_order_id,
            scheduled_for=date(2026, 5, 11),
            status=RecurringOrderOccurrenceStatus.CANCELLED,
            order_id=None,
        )
    )
    await session.flush()

    response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["created_dates"] == ["2026-05-18"]
    assert payload["cancelled_dates"] == ["2026-05-11"]
    await session.flush()

    orders = (
        (
            await session.execute(
                select(Order).where(
                    Order.recurring_order_id == recurring_order_id
                )
            )
        )
        .scalars()
        .all()
    )
    assert [order.date for order in orders] == [date(2026, 5, 18)]


@pytest.mark.asyncio()
async def test_run_recurring_order_pauses_when_business_link_is_missing(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9109
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
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = uuid.UUID(create_response.json())
    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    recurring_order.address_id = None
    await session.flush()

    response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "created_dates": [],
        "already_scheduled_dates": [],
        "cancelled_dates": [],
        "paused": True,
    }
    assert recurring_order.status == RecurringOrderStatus.PAUSED


@pytest.mark.asyncio()
async def test_run_recurring_order_charges_balance_payments(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9110
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, product_price, _ = await setup_test_product(shop_id=shop_id)
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
            "payment_method": "Баланс",
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )

    response = await http_client.post(
        f"{BASE_URL}/{create_response.json()}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )

    assert response.status_code == status.HTTP_200_OK
    await session.flush()
    orders = (
        (
            await session.execute(
                select(Order).where(
                    Order.recurring_order_id
                    == uuid.UUID(create_response.json())
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(orders) == 2
    assert all(order.is_paid for order in orders)

    client = await session.get(Client, client_id)
    assert client is not None
    assert client.balance == -(product_price * 2)


@pytest.mark.asyncio()
async def test_delete_generated_order_cancels_recurring_occurrence(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9111
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
            "schedule_type": "WEEKLY",
            "weekdays": [1],
            "month_days": None,
        },
    )
    recurring_order_id = uuid.UUID(create_response.json())

    run_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=customer_headers(telegram_id),
        json={"include_today": False},
    )
    assert run_response.status_code == status.HTTP_200_OK
    await session.flush()

    occurrence = (
        (
            await session.execute(
                select(RecurringOrderOccurrence).where(
                    RecurringOrderOccurrence.recurring_order_id
                    == recurring_order_id,
                    RecurringOrderOccurrence.scheduled_for
                    == date(2026, 5, 11),
                )
            )
        )
        .scalars()
        .one()
    )
    order_id = occurrence.order_id
    assert order_id is not None

    delete_response = await http_client.delete(
        f"/api/v1/orders/{order_id}",
        headers=customer_headers(telegram_id),
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    session.expire_all()

    occurrence = (
        (
            await session.execute(
                select(RecurringOrderOccurrence).where(
                    RecurringOrderOccurrence.recurring_order_id
                    == recurring_order_id,
                    RecurringOrderOccurrence.scheduled_for
                    == date(2026, 5, 11),
                )
            )
        )
        .scalars()
        .one()
    )
    assert occurrence.status == RecurringOrderOccurrenceStatus.CANCELLED
    assert occurrence.order_id is None


@pytest.mark.asyncio()
async def test_delete_generated_order_can_pause_recurring_order_atomically(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9117
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[1],
    )
    run_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=headers,
        json={"include_today": False},
    )
    assert run_response.status_code == status.HTTP_200_OK
    await session.flush()

    occurrence = (
        (
            await session.execute(
                select(RecurringOrderOccurrence).where(
                    RecurringOrderOccurrence.recurring_order_id
                    == recurring_order_id,
                    RecurringOrderOccurrence.scheduled_for
                    == date(2026, 5, 11),
                )
            )
        )
        .scalars()
        .one()
    )
    order_id = occurrence.order_id
    assert order_id is not None

    delete_response = await http_client.delete(
        f"/api/v1/orders/{order_id}",
        headers=headers,
        params={"pause_recurring_order": True},
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    session.expire_all()

    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    assert recurring_order.status == RecurringOrderStatus.PAUSED


@pytest.mark.asyncio()
async def test_pause_recurring_order_can_cancel_future_generated_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9112
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[5, 1],
    )

    run_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=headers,
        json={"include_today": True},
    )
    assert run_response.status_code == status.HTTP_200_OK
    await session.flush()

    pause_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/pause",
        headers=headers,
        params={"cancel_future_orders": True},
    )

    assert pause_response.status_code == status.HTTP_200_OK
    await session.flush()
    session.expire_all()

    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    assert recurring_order.status == RecurringOrderStatus.PAUSED

    occurrences = (
        (
            await session.execute(
                select(RecurringOrderOccurrence)
                .where(
                    RecurringOrderOccurrence.recurring_order_id
                    == recurring_order_id
                )
                .order_by(RecurringOrderOccurrence.scheduled_for)
            )
        )
        .scalars()
        .all()
    )
    today_occurrence = next(
        row for row in occurrences if row.scheduled_for == date(2026, 5, 8)
    )
    assert today_occurrence.status == RecurringOrderOccurrenceStatus.SCHEDULED
    assert today_occurrence.order_id is not None
    future_occurrences = [
        row for row in occurrences if row.scheduled_for > date(2026, 5, 8)
    ]
    assert future_occurrences
    assert {row.status for row in future_occurrences} == {
        RecurringOrderOccurrenceStatus.CANCELLED
    }
    assert all(row.order_id is None for row in future_occurrences)

    remaining_orders = (
        (
            await session.execute(
                select(Order).where(
                    Order.recurring_order_id == recurring_order_id
                )
            )
        )
        .scalars()
        .all()
    )
    assert [order.date for order in remaining_orders] == [date(2026, 5, 8)]


@pytest.mark.asyncio()
async def test_delete_recurring_order_only_keeps_generated_orders_normal(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9113
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[1],
    )
    run_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=headers,
        json={"include_today": False},
    )
    assert run_response.status_code == status.HTTP_200_OK
    await session.flush()
    order_ids = [
        row.id
        for row in (
            (
                await session.execute(
                    select(Order).where(
                        Order.recurring_order_id == recurring_order_id
                    )
                )
            )
            .scalars()
            .all()
        )
    ]
    assert order_ids

    delete_response = await http_client.delete(
        f"{BASE_URL}/{recurring_order_id}",
        headers=headers,
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    session.expire_all()
    assert await session.get(RecurringOrder, recurring_order_id) is None
    remaining_orders = (
        (await session.execute(select(Order).where(Order.id.in_(order_ids))))
        .scalars()
        .all()
    )
    assert {order.id for order in remaining_orders} == set(order_ids)
    assert all(order.recurring_order_id is None for order in remaining_orders)


@pytest.mark.asyncio()
async def test_delete_recurring_order_with_future_orders_keeps_today_only(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring_order_scheduling_clock.today",
        lambda: date(2026, 5, 8),
    )
    telegram_id = 9114
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[5, 1],
    )
    run_response = await http_client.post(
        f"{BASE_URL}/{recurring_order_id}/run",
        headers=headers,
        json={"include_today": True},
    )
    assert run_response.status_code == status.HTTP_200_OK
    await session.flush()

    delete_response = await http_client.delete(
        f"{BASE_URL}/{recurring_order_id}",
        headers=headers,
        params={"delete_future_orders": True},
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    session.expire_all()

    assert await session.get(RecurringOrder, recurring_order_id) is None
    orders = (
        (
            await session.execute(
                select(Order).where(Order.client_id == client_id)
            )
        )
        .scalars()
        .all()
    )
    assert [order.date for order in orders] == [date(2026, 5, 8)]
    assert orders[0].recurring_order_id is None


@pytest.mark.asyncio()
async def test_delete_product_pauses_affected_recurring_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
) -> None:
    telegram_id = 9115
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[1],
    )

    delete_response = await http_client.delete(
        f"/api/v1/products/{product_id}",
        headers=headers,
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    assert recurring_order.status == RecurringOrderStatus.PAUSED


@pytest.mark.asyncio()
async def test_delete_time_slot_pauses_affected_recurring_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 9116
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    headers = customer_headers(telegram_id)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()
    recurring_order_id = await _create_recurring_order(
        http_client,
        headers,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        weekdays=[1],
    )

    delete_response = await http_client.delete(
        f"/api/v1/time-slots/{time_slot_id}",
        headers=headers,
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()
    recurring_order = await session.get(RecurringOrder, recurring_order_id)
    assert recurring_order is not None
    assert recurring_order.status == RecurringOrderStatus.PAUSED
    assert recurring_order.time_slot_id is None
