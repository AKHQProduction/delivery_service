import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import (
    AddressType,
    ShopRole,
    TimePreference,
)
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    # Create product
    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
    assert order.time_preference == TimePreference.FIRST_HALF.value
    assert order.delivery_phone == "+380501234567"
    assert order.comment == "Доставити до 12:00"

    # Verify delivery address
    assert order.delivery_address["street"] == "Хрещатик"
    assert order.delivery_address["house"] == "10"
    assert order.delivery_address["apartment"] == "5"

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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id_1, _, _, _ = await setup_test_product(shop_id)
    product_id_2, _, _, _ = await setup_test_product(shop_id)
    product_id_3, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.SECOND_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
                "address_type": AddressType.PRIVATE_HOUSE.value,
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
async def test_create_order_with_different_time_preferences(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

    await session.commit()

    headers = customer_headers(telegram_id)

    client_response = await http_client.get(
        url=f"/api/v1/clients/{client_id}", headers=headers
    )
    client_data = client_response.json()
    phone_id = client_data["phones"][0]["id"]
    address_id = client_data["addresses"][0]["id"]

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    # Test FIRST_HALF
    json_first = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response_first = await http_client.post(
        url=BASE_URL, headers=headers, json=json_first
    )
    assert response_first.status_code == status.HTTP_201_CREATED

    # Test SECOND_HALF
    json_second = {
        "client_id": str(client_id),
        "delivery_date": delivery_date,
        "time_preference": TimePreference.SECOND_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
    assert order_first.time_preference == TimePreference.FIRST_HALF.value

    result_second = await session.execute(
        select(Order).where(Order.id == uuid.UUID(order_id_second))
    )
    order_second = result_second.scalar_one()
    assert order_second.time_preference == TimePreference.SECOND_HALF.value


@pytest.mark.asyncio()
async def test_create_order_client_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 5004
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    delivery_date = (datetime.now(UTC).date() + timedelta(days=1)).isoformat()

    json = {
        "client_id": str(uuid.uuid4()),
        "delivery_date": delivery_date,
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": 1,
        "phone_id": 1,
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": 999,  # Non-existent phone_id
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": 999,  # Non-existent address_id
        "phone_id": phone_id,
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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": 1,
        "phone_id": 1,
        "products": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_order_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
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
                "address_type": AddressType.APARTMENT.value,
                "apartment": "5",
            }
        ],
    )

    product_id, _, _, _ = await setup_test_product(shop_id)

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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": address_id,
        "phone_id": phone_id,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
