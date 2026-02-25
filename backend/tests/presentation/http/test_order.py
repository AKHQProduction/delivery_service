import uuid
from collections.abc import Callable
from datetime import UTC, datetime, time, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import (
    PaymentMethod,
    ShopRole,
)
from backend.infrastructure.persistence.tables.clients import ClientAddress
from backend.infrastructure.persistence.tables.orders import Order, OrderItem

BASE_URL = "/api/v1/orders"


@pytest.mark.asyncio()
async def test_create_order_with_single_product(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create client with phone and address
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    # Create product
    product_id, _, _, _ = await setup_test_product(shop_id)

    # Create time slot
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    # Get client to obtain phone_id and address_id
    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [
            {
                "product_id": str(product_id),
                "quantity": 2,
            }
        ],
        "comment": "Доставити до 12:00",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    order_id = response.json()
    assert order_id is not None

    await session.flush()

    # Verify order in database
    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()
    assert order.client_id == client_id
    assert order.shop_id == shop_id
    assert str(order.date) == delivery_date
    assert order.delivery_start_time == time(6, 0)
    assert order.delivery_end_time == time(9, 0)
    assert order.delivery_phone == "+380501234567"
    assert order.comment == "Доставити до 12:00"

    # Verify delivery address
    assert order.delivery_address.street == "Хрещатик"
    assert order.delivery_address.house == "10"
    assert order.delivery_address.apartment == "5"

    # Verify order items
    items_result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == uuid.UUID(order_id))
    )
    items = items_result.scalars().all()
    assert len(items) == 1
    assert items[0].quantity == 2


@pytest.mark.asyncio()
async def test_create_order_with_multiple_products(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5001
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id_1, _, _, _ = await setup_test_product(shop_id)
    product_id_2, _, _, _ = await setup_test_product(shop_id)
    product_id_3, _, _, _ = await setup_test_product(shop_id)

    time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(14, 0),
        end_time=time(20, 0),
    )

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.BANK_TRANSFER,
        "products": [
            {"product_id": str(product_id_1), "quantity": 3},
            {"product_id": str(product_id_2), "quantity": 1},
            {"product_id": str(product_id_3), "quantity": 50},
        ],
        "comment": "Доставка після 14:00",
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    order_id = response.json()

    await session.flush()

    # Verify order items
    items_result = await session.execute(
        select(OrderItem)
        .where(OrderItem.order_id == uuid.UUID(order_id))
        .order_by(OrderItem.id)
    )
    items = items_result.scalars().all()
    assert len(items) == 3
    assert items[0].quantity == 3
    assert items[1].quantity == 1
    assert items[2].quantity == 50


@pytest.mark.asyncio()
async def test_create_order_without_comment(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5002
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "comment": "Private house",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    order_id = response.json()

    await session.flush()

    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()
    assert order.comment is None


@pytest.mark.asyncio()
async def test_create_order_with_different_time_slots(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5003
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

    # Create two time slots
    time_slot_first = await setup_test_time_slot(shop_id=shop_id)
    time_slot_second = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(21, 0),
        end_time=time(23, 0),
    )

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    # Test first time slot
    json_first = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_first),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response_first = await http_client.post(
        url=BASE_URL, headers=headers, json=json_first
    )
    assert response_first.status_code == status.HTTP_201_CREATED

    # Test second time slot
    json_second = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_second),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response_second = await http_client.post(
        url=BASE_URL, headers=headers, json=json_second
    )
    assert response_second.status_code == status.HTTP_201_CREATED

    await session.flush()

    order_id_first = response_first.json()
    order_id_second = response_second.json()

    result_first = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id_first))
    )
    order_first = result_first.scalar_one()
    assert order_first.delivery_start_time == time(6, 0)
    assert order_first.delivery_end_time == time(9, 0)

    result_second = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id_second))
    )
    order_second = result_second.scalar_one()
    assert order_second.delivery_start_time == time(21, 0)
    assert order_second.delivery_end_time == time(23, 0)


@pytest.mark.asyncio()
async def test_create_order_client_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 5004
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(uuid.uuid4()),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": 1,
        "phone_id": 1,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_create_order_product_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_time_slot,
) -> None:
    telegram_id = 5005
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_create_order_phone_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5006
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": 999,  # Non-existent phone_id
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_create_order_address_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5007
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": 999,  # Non-existent address_id
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_create_order_unauthorized(
    http_client: AsyncClient,
) -> None:
    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(uuid.uuid4()),
        "delivery_date": delivery_date,
        "time_slot_id": str(uuid.uuid4()),
        "address_id": 1,
        "phone_id": 1,
        "payment_method": "CASH",
        "products": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_create_order_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5008
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_order_with_past_delivery_date(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5009
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    # Past date
    delivery_date = (datetime.now(UTC).date() - timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio()
async def test_update_order_delivery_date(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5050
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    new_date = (datetime.now(UTC).date() + timedelta(days=5)).isoformat()

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"delivery_date": new_date},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert str(order.date) == new_date


@pytest.mark.asyncio()
async def test_update_order_delivery_date_past_fails(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5051
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    past_date = (datetime.now(UTC).date() - timedelta(days=1)).isoformat()

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"delivery_date": past_date},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio()
async def test_update_order_comment(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5052
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"comment": "Новий коментар"},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.comment == "Новий коментар"


@pytest.mark.asyncio()
async def test_update_order_clear_comment(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5053
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(
        shop_id=shop_id, client_id=client_id, comment="Old comment"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"comment": "EMPTY"},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.comment is None


@pytest.mark.asyncio()
async def test_update_order_payment_method(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5054
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        payment_method=PaymentMethod.CASH,
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"payment_method": PaymentMethod.BANK_TRANSFER},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.payment_method == PaymentMethod.BANK_TRANSFER


@pytest.mark.asyncio()
async def test_update_order_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    setup_test_time_slot,
) -> None:
    telegram_id = 5055
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
    )

    new_time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(14, 0),
        end_time=time(20, 0),
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"time_slot_id": str(new_time_slot_id)},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.delivery_start_time == time(14, 0)
    assert order.delivery_end_time == time(20, 0)


@pytest.mark.asyncio()
async def test_update_order_phone_and_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5056
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111", "+380502222222"],
        addresses=[
            {"street": "Перша", "house": "1", "apartment": "1"},
            {"street": "Друга", "house": "2", "apartment": "2"},
        ],
    )
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_phone="+380501111111",
        delivery_address={"street": "Перша", "house": "1", "apartment": "1"},
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    second_phone_id = client_data["phones"][1]["id"]
    second_address_id = client_data["addresses"][1]["id"]

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "phone_id": second_phone_id,
            "address_id": second_address_id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.delivery_phone == "+380502222222"
    assert order.delivery_address.street == "Друга"


@pytest.mark.asyncio()
async def test_update_order_items_add_new(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_order,
) -> None:
    telegram_id = 5057
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    await setup_test_product(shop_id)
    product_id_2, _, _, _ = await setup_test_product(shop_id)

    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    items_result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    existing_item = items_result.scalars().first()

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "items": [
                {"id": existing_item.id, "quantity": 5},
                {"product_id": str(product_id_2), "quantity": 3},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    items_result = await session.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.id)
    )
    items = items_result.scalars().all()
    assert len(items) == 2


@pytest.mark.asyncio()
async def test_update_order_items_delete(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5058
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        items=[
            {"name": "Product 1", "quantity": 1, "price_per_item": 100},
            {"name": "Product 2", "quantity": 2, "price_per_item": 200},
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    items_result = await session.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.id)
    )
    items = items_result.scalars().all()
    assert len(items) == 2

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "items": [
                {"id": items[0].id, "quantity": 1},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    items_result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    remaining = items_result.scalars().all()
    assert len(remaining) == 1


@pytest.mark.asyncio()
async def test_update_order_items_replace_all(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_order,
) -> None:
    telegram_id = 5059
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    product_id, _, _, _ = await setup_test_product(shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "items": [
                {"product_id": str(product_id), "quantity": 10},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    items_result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = items_result.scalars().all()
    assert len(items) == 1
    assert items[0].quantity == 10


@pytest.mark.asyncio()
async def test_update_order_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 5060
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}",
        headers=headers,
        json={"comment": "test"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_order_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.patch(
        url=f"{BASE_URL}/{uuid.uuid4()}",
        json={"comment": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_update_order_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5061
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"comment": "test"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_order_change_client(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5062
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id_1 = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт 1",
        phones=["+380501111111"],
        addresses=[{"street": "Перша", "house": "1"}],
    )
    client_id_2 = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт 2",
        phones=["+380502222222"],
        addresses=[{"street": "Друга", "house": "2"}],
    )

    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await session.commit()

    headers = customer_headers(telegram_id)

    client2_response = await http_client.get(
        url=f"/api/v1/clients/{client_id_2}", headers=headers
    )
    client2_data = client2_response.json()
    phone_id = client2_data["phones"][0]["id"]
    address_id = client2_data["addresses"][0]["id"]

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "client_id": str(client_id_2),
            "phone_id": phone_id,
            "address_id": address_id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.client_id == client_id_2
    assert order.delivery_phone == "+380502222222"
    assert order.delivery_address.street == "Друга"


@pytest.mark.asyncio()
async def test_update_order_full(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_order,
    setup_test_time_slot,
) -> None:
    telegram_id = 5063
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Тестова", "house": "1"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    new_time_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(14, 0),
        end_time=time(20, 0),
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    new_date = (datetime.now(UTC).date() + timedelta(days=3)).isoformat()

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={
            "delivery_date": new_date,
            "time_slot_id": str(new_time_slot_id),
            "phone_id": phone_id,
            "address_id": address_id,
            "comment": "Повне оновлення",
            "payment_method": PaymentMethod.CASH,
            "items": [
                {"product_id": str(product_id), "quantity": 7},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert str(order.date) == new_date
    assert order.delivery_start_time == time(14, 0)
    assert order.delivery_end_time == time(20, 0)
    assert order.comment == "Повне оновлення"
    assert order.payment_method == PaymentMethod.CASH


@pytest.mark.asyncio()
async def test_delete_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    delete_response = await http_client.delete(
        url=f"{BASE_URL}/{order_id}", headers=headers
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_delete_order_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_test_client,
    setup_test_order,
    create_user,
    create_telegram_account,
    create_role,
    create_shop_membership,
    create_shop,
) -> None:
    courier_telegram_id = 5102

    shop_id = await create_shop()

    courier_user_id = await create_user()
    await create_telegram_account(
        user_id=courier_user_id,
        telegram_id=courier_telegram_id,
        full_name="Courier User",
    )
    courier_role_id = await create_role(role_id=1, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=courier_user_id, shop_id=shop_id, role_id=courier_role_id
    )

    client_id = await setup_test_client(shop_id=shop_id)
    order_id = await setup_test_order(shop_id=shop_id, client_id=client_id)
    await session.commit()

    courier_headers = customer_headers(courier_telegram_id)

    delete_response = await http_client.delete(
        url=f"{BASE_URL}/{order_id}", headers=courier_headers
    )

    assert delete_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5200
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Тестовий Клієнт",
    )

    delivery_date = datetime.now(UTC).date() + timedelta(days=1)
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
        delivery_phone="+380501234567",
        delivery_address={
            "street": "Хрещатик",
            "house": "10",
            "apartment": "5",
        },
        comment="Test comment",
        items=[{"name": "Test Product", "quantity": 2, "price_per_item": 100}],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    get_response = await http_client.get(
        url=f"{BASE_URL}/{order_id}", headers=headers
    )

    assert get_response.status_code == status.HTTP_200_OK

    order_data = get_response.json()
    assert order_data["order_id"] == str(order_id)
    assert order_data["client_id"] == str(client_id)
    assert order_data["client_name"] == "Тестовий Клієнт"
    assert order_data["date"] == delivery_date.strftime("%d.%m.%Y")
    assert order_data["time_slot"] == "09:00-14:00"
    assert order_data["delivery_phone"] == "+380501234567"
    assert order_data["delivery_address"]["street"] == "Хрещатик"
    assert order_data["comment"] == "Test comment"
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["quantity"] == 2


@pytest.mark.asyncio()
async def test_get_order_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 5201
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)
    non_existent_id = str(uuid.uuid4())

    response = await http_client.get(
        url=f"{BASE_URL}/{non_existent_id}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_all_orders(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5300
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    for i in range(3):
        delivery_date = datetime.now(UTC).date() + timedelta(days=i + 1)
        await setup_test_order(
            shop_id=shop_id, client_id=client_id, delivery_date=delivery_date
        )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(url=f"{BASE_URL}/all", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 3


@pytest.mark.asyncio()
async def test_get_all_orders_with_date_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5301
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    tomorrow = datetime.now(UTC).date() + timedelta(days=1)
    day_after = datetime.now(UTC).date() + timedelta(days=2)

    for delivery_date in [tomorrow, tomorrow, day_after]:
        await setup_test_order(
            shop_id=shop_id, client_id=client_id, delivery_date=delivery_date
        )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(
        order["date"] == tomorrow.strftime("%d.%m.%Y") for order in orders
    )


@pytest.mark.asyncio()
async def test_get_all_orders_with_delivery_time_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5302
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    # Create orders with different delivery times
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_start_time=time(14, 0),
        delivery_end_time=time(20, 0),
    )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"delivery_start_time": "09:00:00"},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(order["time_slot"].startswith("09:00") for order in orders)


@pytest.mark.asyncio()
async def test_get_all_orders_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5303
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    for i in range(5):
        delivery_date = datetime.now(UTC).date() + timedelta(days=i + 1)
        await setup_test_order(
            shop_id=shop_id, client_id=client_id, delivery_date=delivery_date
        )

    await session.commit()

    headers = customer_headers(telegram_id)

    page1 = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 2, "offset": 0},
    )
    page2 = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 2, "offset": 2},
    )
    page3 = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 2, "offset": 4},
    )

    assert page1.status_code == status.HTTP_200_OK
    assert page2.status_code == status.HTTP_200_OK
    assert page3.status_code == status.HTTP_200_OK

    assert len(page1.json()) == 2
    assert len(page2.json()) == 2
    assert len(page3.json()) == 1

    all_ids = [
        o["order_id"] for o in page1.json() + page2.json() + page3.json()
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.asyncio()
async def test_get_all_orders_pagination_no_duplicates_same_date(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5350
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    same_date = datetime.now(UTC).date() + timedelta(days=1)
    for _ in range(10):
        await setup_test_order(
            shop_id=shop_id,
            client_id=client_id,
            delivery_date=same_date,
        )

    await session.commit()

    headers = customer_headers(telegram_id)

    all_order_ids: list[str] = []
    for offset in range(0, 10, 2):
        response = await http_client.get(
            url=f"{BASE_URL}/all",
            headers=headers,
            params={"limit": 2, "offset": offset},
        )
        assert response.status_code == status.HTTP_200_OK
        page_ids = [o["order_id"] for o in response.json()]
        all_order_ids.extend(page_ids)

    assert len(all_order_ids) == 10
    assert len(all_order_ids) == len(set(all_order_ids))


@pytest.mark.asyncio()
async def test_get_all_orders_filters_by_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_test_client,
    setup_test_order,
    create_user,
    create_telegram_account,
    create_role,
    create_shop_membership,
    create_shop,
) -> None:
    user1_telegram_id = 5304
    user2_telegram_id = 5305

    # Create shared role
    role_id = await create_role(role_id=1, name=ShopRole.OWNER)

    # User 1 with shop 1
    shop_id_1 = await create_shop()
    user_id_1 = await create_user()
    await create_telegram_account(
        user_id=user_id_1, telegram_id=user1_telegram_id, full_name="User 1"
    )
    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id_1, role_id=role_id
    )

    # User 2 with shop 2
    shop_id_2 = await create_shop()
    user_id_2 = await create_user()
    await create_telegram_account(
        user_id=user_id_2, telegram_id=user2_telegram_id, full_name="User 2"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id_2, role_id=role_id
    )

    client_id_1 = await setup_test_client(shop_id=shop_id_1)
    client_id_2 = await setup_test_client(shop_id=shop_id_2)

    for _ in range(2):
        await setup_test_order(shop_id=shop_id_1, client_id=client_id_1)

    for _ in range(3):
        await setup_test_order(shop_id=shop_id_2, client_id=client_id_2)

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
    assert len(response_2.json()) == 3


@pytest.mark.asyncio()
async def test_get_all_orders_with_client_name_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5306
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id_1 = await setup_test_client(
        shop_id=shop_id, full_name="Іван Іванов"
    )
    client_id_2 = await setup_test_client(
        shop_id=shop_id, full_name="Петро Петренко"
    )

    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_2)

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"client_name": "Іван"},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(order["client_name"] == "Іван Іванов" for order in orders)


@pytest.mark.asyncio()
async def test_get_all_orders_with_combined_client_filters(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5308
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id_1 = await setup_test_client(
        shop_id=shop_id, full_name="Іван Іванов"
    )
    client_id_2 = await setup_test_client(
        shop_id=shop_id, full_name="Петро Петренко"
    )

    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_2)

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"client_name": "Іван"},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 1


@pytest.mark.asyncio()
async def test_get_order_stats(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5400
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
        items=[{"name": "Product 1", "quantity": 2, "price_per_item": 100}],
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
        items=[{"name": "Product 2", "quantity": 3, "price_per_item": 50}],
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(14, 0),
        delivery_end_time=time(21, 0),
        items=[{"name": "Product 3", "quantity": 1, "price_per_item": 200}],
    )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/stats",
        headers=headers,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["total_orders"] == 3
    assert len(stats["time_slot_stats"]) == 2
    assert stats["time_slot_stats"][0]["time_slot"] == "09:00-14:00"
    assert stats["time_slot_stats"][0]["total"] == 2
    assert stats["time_slot_stats"][1]["time_slot"] == "14:00-21:00"
    assert stats["time_slot_stats"][1]["total"] == 1
    # 2*100 + 3*50 + 1*200 = 200 + 150 + 200 = 550
    assert stats["total_orders_sum"] == 550


@pytest.mark.asyncio()
async def test_get_order_stats_with_multiple_items_per_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5404
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(shop_id=shop_id)

    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        delivery_start_time=time(9, 0),
        delivery_end_time=time(14, 0),
        items=[
            {"name": "Product 1", "quantity": 2, "price_per_item": 100},
            {"name": "Product 2", "quantity": 1, "price_per_item": 200},
            {"name": "Product 3", "quantity": 3, "price_per_item": 50},
        ],
    )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/stats",
        headers=headers,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["total_orders"] == 1
    assert len(stats["time_slot_stats"]) == 2
    assert stats["time_slot_stats"][0]["time_slot"] == "09:00-14:00"
    assert stats["time_slot_stats"][0]["total"] == 1
    assert stats["time_slot_stats"][1]["time_slot"] == "14:00-21:00"
    assert stats["time_slot_stats"][1]["total"] == 0
    # 2*100 + 1*200 + 3*50 = 200 + 200 + 150 = 550
    assert stats["total_orders_sum"] == 550


@pytest.mark.asyncio()
async def test_get_order_stats_empty(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 5401
    _, _ = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    await session.commit()

    headers = customer_headers(telegram_id)
    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    response = await http_client.get(
        url=f"{BASE_URL}/stats",
        headers=headers,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["total_orders"] == 0
    assert len(stats["time_slot_stats"]) == 2
    assert stats["time_slot_stats"][0]["total"] == 0
    assert stats["time_slot_stats"][1]["total"] == 0
    assert stats["total_orders_sum"] == 0


@pytest.mark.asyncio()
async def test_get_order_stats_filters_by_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_test_client,
    setup_test_order,
    setup_test_time_slot,
    create_user,
    create_telegram_account,
    create_role,
    create_shop_membership,
    create_shop,
) -> None:
    user1_telegram_id = 5402
    user2_telegram_id = 5403

    role_id = await create_role(role_id=1, name=ShopRole.OWNER)

    # User 1 with shop 1
    shop_id_1 = await create_shop()
    user_id_1 = await create_user()
    await create_telegram_account(
        user_id=user_id_1, telegram_id=user1_telegram_id, full_name="User 1"
    )
    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id_1, role_id=role_id
    )

    # User 2 with shop 2
    shop_id_2 = await create_shop()
    user_id_2 = await create_user()
    await create_telegram_account(
        user_id=user_id_2, telegram_id=user2_telegram_id, full_name="User 2"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id_2, role_id=role_id
    )

    await setup_test_time_slot(shop_id=shop_id_1)
    await setup_test_time_slot(shop_id=shop_id_2)

    client_id_1 = await setup_test_client(shop_id=shop_id_1)
    client_id_2 = await setup_test_client(shop_id=shop_id_2)

    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    # 2 orders for shop 1
    for _ in range(2):
        await setup_test_order(
            shop_id=shop_id_1,
            client_id=client_id_1,
            delivery_date=tomorrow,
            items=[{"name": "Product", "quantity": 1, "price_per_item": 100}],
        )

    # 3 orders for shop 2
    for _ in range(3):
        await setup_test_order(
            shop_id=shop_id_2,
            client_id=client_id_2,
            delivery_date=tomorrow,
            items=[{"name": "Product", "quantity": 1, "price_per_item": 100}],
        )

    await session.commit()

    headers_1 = customer_headers(user1_telegram_id)
    headers_2 = customer_headers(user2_telegram_id)

    response_1 = await http_client.get(
        url=f"{BASE_URL}/stats",
        headers=headers_1,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )
    response_2 = await http_client.get(
        url=f"{BASE_URL}/stats",
        headers=headers_2,
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK

    stats_1 = response_1.json()
    stats_2 = response_2.json()

    assert stats_1["total_orders"] == 2
    assert stats_2["total_orders"] == 3


@pytest.mark.asyncio()
async def test_get_order_stats_unauthorized(
    http_client: AsyncClient,
) -> None:
    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    response = await http_client.get(
        url=f"{BASE_URL}/stats",
        params={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_generate_orders_pdf(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 6100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Тест Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Тестова",
                "house": "1",
                "apartment": "1",
            }
        ],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    order_json = {
        "client_id": str(client_id),
        "delivery_date": tomorrow,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }
    await http_client.post(url=BASE_URL, headers=headers, json=order_json)
    await session.commit()

    response = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        headers=headers,
        json={"delivery_date": tomorrow, "doc_type": "ORDER_LIST"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "file_id" in data
    assert "filename" in data
    assert data["filename"] == f"orders_{tomorrow}.pdf"


@pytest.mark.asyncio()
async def test_generate_orders_pdf_with_time_slot_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 6110
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Тест Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Тестова",
                "house": "1",
                "apartment": "1",
            }
        ],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)

    time_slot_1 = await setup_test_time_slot(shop_id=shop_id)
    time_slot_2 = await setup_test_time_slot(
        shop_id=shop_id, start_time=time(12, 0), end_time=time(15, 0)
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    for ts_id in [time_slot_1, time_slot_2]:
        await http_client.post(
            url=BASE_URL,
            headers=headers,
            json={
                "client_id": str(client_id),
                "delivery_date": tomorrow,
                "time_slot_id": str(ts_id),
                "address_id": address_id,
                "phone_id": phone_id,
                "payment_method": PaymentMethod.CASH,
                "products": [{"product_id": str(product_id), "quantity": 1}],
            },
        )
    await session.commit()

    response_all = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        headers=headers,
        json={"delivery_date": tomorrow, "doc_type": "ORDER_LIST"},
    )
    assert response_all.status_code == status.HTTP_200_OK

    response_filtered = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        headers=headers,
        json={
            "delivery_date": tomorrow,
            "doc_type": "ORDER_LIST",
            "time_slot_id": str(time_slot_1),
        },
    )
    assert response_filtered.status_code == status.HTTP_200_OK
    assert "file_id" in response_filtered.json()


@pytest.mark.asyncio()
async def test_generate_orders_pdf_unauthorized(
    http_client: AsyncClient,
) -> None:
    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    response = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        json={
            "delivery_date": tomorrow.isoformat(),
            "doc_type": "ORDER_LIST",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_download_orders_pdf(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 6101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Тест Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Тестова",
                "house": "1",
                "apartment": "1",
            }
        ],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    order_json = {
        "client_id": str(client_id),
        "delivery_date": tomorrow,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }
    await http_client.post(url=BASE_URL, headers=headers, json=order_json)
    await session.commit()

    generate_response = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        headers=headers,
        json={"delivery_date": tomorrow, "doc_type": "ORDER_LIST"},
    )
    file_id = generate_response.json()["file_id"]

    download_response = await http_client.get(
        url=f"{BASE_URL}/export/pdf/download/{file_id}",
    )

    assert download_response.status_code == status.HTTP_200_OK
    assert download_response.headers["content-type"] == "application/pdf"
    assert "content-disposition" in download_response.headers


@pytest.mark.asyncio()
async def test_download_orders_pdf_not_found(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(
        url=f"{BASE_URL}/export/pdf/download/nonexistent-file-id",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_order_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.delete(url=f"{BASE_URL}/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_delete_order_not_found_returns_ok(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 5103
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{uuid.uuid4()}", headers=headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_get_order_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/{uuid.uuid4()}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_get_all_orders_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/all")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_generate_orders_pdf_as_courier_allowed(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 6102
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    await session.commit()

    headers = customer_headers(telegram_id)
    tomorrow = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    response = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        headers=headers,
        json={"delivery_date": tomorrow, "doc_type": "ORDER_LIST"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
async def test_create_order_with_district_in_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
    setup_test_district,
) -> None:
    telegram_id = 6200
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    district_id = await setup_test_district(
        shop_id=shop_id, name="Шевченківський"
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт з Районом",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
                "district_id": district_id,
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    order_id = response.json()

    await session.flush()

    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()

    assert order.delivery_address.street == "Хрещатик"
    assert order.delivery_address.district == "Шевченківський"


@pytest.mark.asyncio()
async def test_create_order_without_district_in_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 6201
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт без Району",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    order_id = response.json()

    await session.flush()

    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()

    assert order.delivery_address.street == "Хрещатик"
    assert order.delivery_address.district is None


@pytest.mark.asyncio()
async def test_update_order_address_with_district(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
    setup_test_district,
) -> None:
    telegram_id = 6202
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    district_id = await setup_test_district(
        shop_id=shop_id, name="Подільський"
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111", "+380502222222"],
        addresses=[
            {"street": "Перша", "house": "1", "apartment": "1"},
            {
                "street": "Друга",
                "house": "2",
                "apartment": "2",
                "district_id": district_id,
            },
        ],
    )
    order_id = await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_phone="+380501111111",
        delivery_address={"street": "Перша", "house": "1", "apartment": "1"},
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    second_address_id = client_data["addresses"][1]["id"]

    response = await http_client.patch(
        url=f"{BASE_URL}/{order_id}",
        headers=headers,
        json={"address_id": second_address_id},
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.delivery_address.street == "Друга"
    assert order.delivery_address.district == "Подільський"


GEOCODER_GEOCODE = "backend.application.services.geocoder.Geocoder.geocode"


@pytest.mark.asyncio()
async def test_create_order_geocodes_address_without_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5100
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, shop_city="Київ"
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_resp = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_resp.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    fake_coords = CoordinatesDTO(latitude=50.45, longitude=30.52)

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    with patch(
        GEOCODER_GEOCODE,
        new_callable=AsyncMock,
        return_value=fake_coords,
    ) as mock_geocode:
        response = await http_client.post(
            url=BASE_URL, headers=headers, json=json
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_geocode.assert_called_once_with(
            "Хрещатик", "10", "Київ", require_house=False
        )

    order_id = response.json()
    await session.flush()

    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()
    assert order.delivery_address.coordinates is not None
    assert order.delivery_address.coordinates.latitude == 50.45
    assert order.delivery_address.coordinates.longitude == 30.52

    addr_result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addr = addr_result.scalar_one()
    assert addr.latitude == 50.45
    assert addr.longitude == 30.52


@pytest.mark.asyncio()
async def test_create_order_skips_geocoding_when_address_has_coords(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    setup_test_time_slot,
) -> None:
    telegram_id = 5101
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, shop_city="Київ"
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.4501,
                "longitude": 30.5234,
            }
        ],
    )
    product_id, _, _, _ = await setup_test_product(shop_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    client_resp = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_resp.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_slot_id": str(time_slot_id),
        "address_id": address_id,
        "phone_id": phone_id,
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    with patch(
        GEOCODER_GEOCODE,
        new_callable=AsyncMock,
    ) as mock_geocode:
        response = await http_client.post(
            url=BASE_URL, headers=headers, json=json
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_geocode.assert_not_called()

    order_id = response.json()
    await session.flush()

    result = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalar_one()
    assert order.delivery_address.coordinates is not None
    assert order.delivery_address.coordinates.latitude == 50.4501
