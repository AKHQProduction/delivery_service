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
    PaymentMethod,
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
        "payment_method": PaymentMethod.CASH,
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
        "time_preference": TimePreference.FIRST_HALF,
        "address_id": 1,
        "phone_id": 1,
        "payment_method": "CASH",
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
        "payment_method": PaymentMethod.CASH,
        "products": [{"product_id": str(product_id), "quantity": 1}],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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

    assert delete_response.status_code == status.HTTP_200_OK

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
        time_preference=TimePreference.FIRST_HALF,
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
    assert order_data["date"] == delivery_date.isoformat()
    assert order_data["time_preference"] == TimePreference.FIRST_HALF.value
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
        params={"delivery_date": tomorrow.isoformat()},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(order["date"] == tomorrow.isoformat() for order in orders)


@pytest.mark.asyncio()
async def test_get_all_orders_with_time_preference_filter(
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

    for time_pref in [
        TimePreference.FIRST_HALF,
        TimePreference.FIRST_HALF,
        TimePreference.SECOND_HALF,
    ]:
        await setup_test_order(
            shop_id=shop_id, client_id=client_id, time_preference=time_pref
        )

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"time_preference": TimePreference.FIRST_HALF.value},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(
        order["time_preference"] == TimePreference.FIRST_HALF.value
        for order in orders
    )


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
async def test_get_all_orders_with_custom_id_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_order,
) -> None:
    telegram_id = 5307
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id_1 = await setup_test_client(
        shop_id=shop_id, full_name="Клієнт 1", custom_id="VIP-001"
    )
    client_id_2 = await setup_test_client(
        shop_id=shop_id, full_name="Клієнт 2", custom_id="REG-002"
    )

    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_2)

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"custom_id": "VIP"},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2
    assert all(order["client_name"] == "Клієнт 1" for order in orders)


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
        shop_id=shop_id, full_name="Іван Іванов", custom_id="VIP-001"
    )
    client_id_2 = await setup_test_client(
        shop_id=shop_id, full_name="Петро Петренко", custom_id="REG-002"
    )

    await setup_test_order(shop_id=shop_id, client_id=client_id_1)
    await setup_test_order(shop_id=shop_id, client_id=client_id_2)

    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"client_name": "Іван", "custom_id": "REG"},
    )

    assert response.status_code == status.HTTP_200_OK
    orders = response.json()
    assert len(orders) == 2


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
        time_preference=TimePreference.FIRST_HALF,
        items=[{"name": "Product 1", "quantity": 2, "price_per_item": 100}],
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        time_preference=TimePreference.FIRST_HALF,
        items=[{"name": "Product 2", "quantity": 3, "price_per_item": 50}],
    )
    await setup_test_order(
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=tomorrow,
        time_preference=TimePreference.SECOND_HALF,
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
    assert stats["total_orders_in_first_half"] == 2
    assert stats["total_orders_in_second_half"] == 1
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
        time_preference=TimePreference.FIRST_HALF,
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
    assert stats["total_orders_in_first_half"] == 1
    assert stats["total_orders_in_second_half"] == 0
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
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
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
    assert stats["total_orders_in_first_half"] == 0
    assert stats["total_orders_in_second_half"] == 0
    assert stats["total_orders_sum"] == 0


@pytest.mark.asyncio()
async def test_get_order_stats_filters_by_shop(
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

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_generate_orders_pdf(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
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
        "time_preference": TimePreference.FIRST_HALF,
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
        params={"delivery_date": tomorrow},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "file_id" in data
    assert "filename" in data
    assert data["filename"] == f"orders_{tomorrow}.pdf"


@pytest.mark.asyncio()
async def test_generate_orders_pdf_unauthorized(
    http_client: AsyncClient,
) -> None:
    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    response = await http_client.post(
        url=f"{BASE_URL}/export/pdf/generate",
        params={"delivery_date": tomorrow.isoformat()},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_download_orders_pdf(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
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
        "time_preference": TimePreference.FIRST_HALF,
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
        params={"delivery_date": tomorrow},
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
