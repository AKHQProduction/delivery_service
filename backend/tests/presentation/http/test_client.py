import uuid
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.vars import ShopRole
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)

BASE_URL = "/api/v1/clients"


@pytest.mark.asyncio()
async def test_create_client_with_apartment(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Іван Іванов",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
                "entrance": "1",
                "floor": "2",
                "intercom": "5",
            }
        ],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()
    assert client_id is not None

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == uuid.UUID(client_id))
    )
    client = result.scalar_one()
    assert client.full_name == "Іван Іванов"

    phone_result = await session.execute(
        select(ClientPhone).where(
            ClientPhone.client_id == uuid.UUID(client_id)
        )
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380501234567"
    assert phones[0].is_primary is True

    address_result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].street == "Хрещатик"
    assert addresses[0].house == "10"
    assert addresses[0].apartment == "5"
    assert addresses[0].comment is None
    assert addresses[0].is_primary is True


@pytest.mark.asyncio()
async def test_create_client_with_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1010
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Клієнт з Координатами",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
                "apartment": "5",
                "coordinates": {
                    "latitude": 50.4501,
                    "longitude": 30.5234,
                },
            }
        ],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].latitude == 50.4501
    assert addresses[0].longitude == 30.5234


@pytest.mark.asyncio()
async def test_create_client_without_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1011
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Клієнт без Координат",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
            }
        ],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].latitude is None
    assert addresses[0].longitude is None


@pytest.mark.asyncio()
async def test_create_client_with_private_house(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1001
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Петро Петренко",
        "phones": [{"number": "+380931234567"}],
        "addresses": [
            {
                "street": "Заміська",
                "house": "15А",
                "comment": "Private house",
            }
        ],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()
    assert client_id is not None

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == uuid.UUID(client_id))
    )
    client = result.scalar_one()
    assert client.full_name == "Петро Петренко"

    address_result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].street == "Заміська"
    assert addresses[0].house == "15А"
    assert addresses[0].comment == "Private house"
    assert addresses[0].apartment is None
    assert addresses[0].is_primary is True


@pytest.mark.asyncio()
async def test_create_client_with_multiple_phones_and_addresses(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1002
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Марія Марченко",
        "phones": [
            {"number": "+380671234567"},
            {"number": "+380631234567"},
            {"number": "+380501111111"},
        ],
        "addresses": [
            {
                "street": "Грушевського",
                "house": "5",
                "apartment": "10",
            },
            {
                "street": "Садова",
                "house": "22Б",
                "comment": "Private house",
            },
        ],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone)
        .where(ClientPhone.client_id == uuid.UUID(client_id))
        .order_by(ClientPhone.id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 3
    assert phones[0].number == "+380671234567"
    assert phones[0].is_primary is True
    assert phones[1].number == "+380631234567"
    assert phones[1].is_primary is False
    assert phones[2].number == "+380501111111"
    assert phones[2].is_primary is False

    address_result = await session.execute(
        select(ClientAddress)
        .where(ClientAddress.client_id == uuid.UUID(client_id))
        .order_by(ClientAddress.id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 2
    assert addresses[0].street == "Грушевського"
    assert addresses[0].is_primary is True
    assert addresses[1].street == "Садова"
    assert addresses[1].is_primary is False


@pytest.mark.asyncio()
async def test_create_client_without_phones_and_addresses(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1003
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Олексій Олексієнко",
        "phones": [],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == uuid.UUID(client_id))
    )
    client = result.scalar_one()
    assert client.full_name == "Олексій Олексієнко"

    phone_result = await session.execute(
        select(ClientPhone).where(
            ClientPhone.client_id == uuid.UUID(client_id)
        )
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 0

    address_result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 0


@pytest.mark.asyncio()
async def test_create_client_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {
        "full_name": "Test User",
        "phones": [{"number": "+380501234567"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_client_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1004
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Test User",
        "phones": [{"number": "+380501234567"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_client_by_id(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create client directly in DB
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Тестовий Клієнт",
        phones=["+380501234567", "+380507654321"],
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

    # Get the client by ID
    response = await http_client.get(
        url=f"{BASE_URL}/{client_id}", headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["client_id"] == str(client_id)
    assert data["full_name"] == "Тестовий Клієнт"
    assert len(data["phones"]) == 2
    assert data["phones"][0]["number"] == "+380501234567"
    assert data["phones"][0]["is_primary"] is True
    assert data["phones"][1]["number"] == "+380507654321"
    assert data["phones"][1]["is_primary"] is False
    assert len(data["addresses"]) == 1
    assert data["addresses"][0]["street"] == "Хрещатик"
    assert data["addresses"][0]["is_primary"] is True


@pytest.mark.asyncio()
async def test_get_client_by_id_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2001
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    non_existent_id = str(uuid.uuid4())

    response = await http_client.get(
        url=f"{BASE_URL}/{non_existent_id}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_client_unauthorized(
    http_client: AsyncClient,
) -> None:
    client_id = str(uuid.uuid4())

    response = await http_client.get(url=f"{BASE_URL}/{client_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_all_clients(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create three clients directly in DB
    await setup_test_client(
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=["+380501111111"],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=["+380502222222"],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Віктор Вікторенко",
        phones=["+380503333333"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    # Get all clients
    response = await http_client.get(url=f"{BASE_URL}/all", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["full_name"] == "Анна Антоненко"
    assert data[1]["full_name"] == "Борис Борисенко"
    assert data[2]["full_name"] == "Віктор Вікторенко"


@pytest.mark.asyncio()
async def test_get_all_clients_filter_by_full_name(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create clients directly in DB
    await setup_test_client(
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=["+380501111111"],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=["+380502222222"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    # Filter by full name
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"full_name": "Анна"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Анна Антоненко"


@pytest.mark.asyncio()
async def test_get_all_clients_filter_by_phone(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2102
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create clients directly in DB
    await setup_test_client(
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=["+380501111111"],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=["+380502222222"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    # Filter by phone
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"phone": "1111"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Анна Антоненко"


@pytest.mark.asyncio()
async def test_get_all_clients_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2104
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create 5 clients directly in DB
    for i in range(5):
        await setup_test_client(
            shop_id=shop_id,
            full_name=f"Client {i:02d}",
        )
    await session.commit()

    headers = customer_headers(telegram_id)

    # Get first 3 clients
    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 3, "offset": 0},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

    # Get next 2 clients
    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 3, "offset": 3},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio()
async def test_get_all_clients_with_sorting(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2105
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create clients directly in DB
    await setup_test_client(shop_id=shop_id, full_name="Віктор")
    await setup_test_client(shop_id=shop_id, full_name="Анна")
    await setup_test_client(shop_id=shop_id, full_name="Борис")
    await session.commit()

    headers = customer_headers(telegram_id)

    # Sort ascending (default)
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"order": "ASC"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["full_name"] == "Анна"
    assert data[1]["full_name"] == "Борис"
    assert data[2]["full_name"] == "Віктор"

    # Sort descending
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"order": "DESC"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["full_name"] == "Віктор"
    assert data[1]["full_name"] == "Борис"
    assert data[2]["full_name"] == "Анна"


@pytest.mark.asyncio()
async def test_get_all_clients_unauthorized(
    http_client: AsyncClient,
) -> None:
    response = await http_client.get(url=f"{BASE_URL}/all")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_product(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    client_id = await setup_test_client(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{client_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()

    deleted_entity = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    assert deleted_entity.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_edit_client_full_name(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Оригінальне Ім'я",
        phones=["+380501111111", "+380502222222"],
        addresses=[
            {
                "street": "Оригінальна вулиця",
                "house": "1",
                "apartment": "10",
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"full_name": "Оновлене Ім'я"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one()
    assert client.full_name == "Оновлене Ім'я"


@pytest.mark.asyncio()
async def test_edit_client_phones(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3002
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
        phones=["+380501111111", "+380502222222"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "phones": [
            {"number": "+380509999999", "is_primary": True},
            {"number": "+380508888888", "is_primary": False},
            {"number": "+380507777777", "is_primary": False},
        ]
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )
    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone)
        .where(ClientPhone.client_id == client_id)
        .order_by(ClientPhone.id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 3
    assert phones[0].number == "+380509999999"
    assert phones[0].is_primary is True
    assert phones[1].number == "+380508888888"
    assert phones[1].is_primary is False
    assert phones[2].number == "+380507777777"
    assert phones[2].is_primary is False


@pytest.mark.asyncio()
async def test_edit_client_addresses(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3003
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
        addresses=[
            {
                "street": "Стара вулиця",
                "house": "1",
                "apartment": "10",
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "addresses": [
            {
                "street": "Нова вулиця",
                "house": "100",
                "comment": "Private house",
                "is_primary": True,
            },
            {
                "street": "Ще одна вулиця",
                "house": "200",
                "apartment": "50",
                "is_primary": False,
            },
        ]
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress)
        .where(ClientAddress.client_id == client_id)
        .order_by(ClientAddress.id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 2
    assert addresses[0].street == "Нова вулиця"
    assert addresses[0].house == "100"
    assert addresses[0].comment == "Private house"
    assert addresses[0].is_primary is True
    assert addresses[1].street == "Ще одна вулиця"
    assert addresses[1].is_primary is False


@pytest.mark.asyncio()
async def test_edit_client_add_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3009
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        addresses=[
            {
                "street": "Вулиця",
                "house": "1",
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "addresses": [
            {
                "street": "Вулиця",
                "house": "1",
                "coordinates": {
                    "latitude": 50.4501,
                    "longitude": 30.5234,
                },
                "is_primary": True,
            }
        ]
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].latitude == 50.4501
    assert addresses[0].longitude == 30.5234


@pytest.mark.asyncio()
async def test_edit_client_remove_coordinates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3010
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        addresses=[
            {
                "street": "Вулиця",
                "house": "1",
                "latitude": 50.4501,
                "longitude": 30.5234,
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "addresses": [
            {
                "street": "Вулиця",
                "house": "1",
                "is_primary": True,
            }
        ]
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].latitude is None
    assert addresses[0].longitude is None


@pytest.mark.asyncio()
async def test_get_client_coordinates_in_response(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3011
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт з Координатами",
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
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/{client_id}", headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["addresses"]) == 1
    assert data["addresses"][0]["coordinates"]["latitude"] == 50.4501
    assert data["addresses"][0]["coordinates"]["longitude"] == 30.5234


@pytest.mark.asyncio()
async def test_edit_client_all_fields(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3004
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Старе Ім'я",
        phones=["+380501111111"],
        addresses=[
            {
                "street": "Стара вулиця",
                "house": "1",
                "apartment": "10",
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Повністю Нове Ім'я",
        "phones": [{"number": "+380501234567", "is_primary": True}],
        "addresses": [
            {
                "street": "Повністю нова вулиця",
                "house": "999",
                "comment": "Private house",
                "is_primary": True,
            }
        ],
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one()
    assert client.full_name == "Повністю Нове Ім'я"

    phone_result = await session.execute(
        select(ClientPhone).where(ClientPhone.client_id == client_id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380501234567"

    address_result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].street == "Повністю нова вулиця"


@pytest.mark.asyncio()
async def test_edit_client_clear_phones(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3005
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
        phones=["+380501111111", "+380502222222"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json: dict[str, list[Any]] = {"phones": []}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone).where(ClientPhone.client_id == client_id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 0


@pytest.mark.asyncio()
async def test_edit_client_clear_addresses(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3006
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
        addresses=[
            {
                "street": "Вулиця",
                "house": "1",
                "apartment": "10",
            }
        ],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json: dict[str, list[Any]] = {"addresses": []}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    address_result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = address_result.scalars().all()
    assert len(addresses) == 0


@pytest.mark.asyncio()
async def test_edit_client_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 3007
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    non_existent_id = str(uuid.uuid4())

    json = {"full_name": "Нове Ім'я"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{non_existent_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_edit_client_unauthorized(
    http_client: AsyncClient,
) -> None:
    client_id = str(uuid.uuid4())

    json = {"full_name": "Нове Ім'я"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", json=json
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_client_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3008
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"full_name": "Нове Ім'я"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_create_client_with_duplicate_phone_returns_409(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 3100
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json1 = {
        "full_name": "Перший Клієнт",
        "phones": [{"number": "+380991234567"}],
        "addresses": [],
    }

    response1 = await http_client.post(
        url=BASE_URL, headers=headers, json=json1
    )
    assert response1.status_code == status.HTTP_201_CREATED

    await session.flush()

    json2 = {
        "full_name": "Другий Клієнт",
        "phones": [{"number": "+380991234567"}],
        "addresses": [],
    }

    response2 = await http_client.post(
        url=BASE_URL, headers=headers, json=json2
    )

    assert response2.status_code == status.HTTP_409_CONFLICT
    data = response2.json()
    assert data["code"] == "duplicate_phones"
    assert len(data["duplicates"]) == 1
    assert data["duplicates"][0]["phone_number"] == "+380991234567"
    assert (
        data["duplicates"][0]["existing_clients"][0]["full_name"]
        == "Перший Клієнт"
    )


@pytest.mark.asyncio()
async def test_create_client_with_duplicate_phone_confirmed(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 3103
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json1 = {
        "full_name": "Перший Клієнт",
        "phones": [{"number": "+380991234567"}],
        "addresses": [],
    }

    response1 = await http_client.post(
        url=BASE_URL, headers=headers, json=json1
    )
    assert response1.status_code == status.HTTP_201_CREATED

    await session.flush()

    json2 = {
        "full_name": "Другий Клієнт",
        "phones": [{"number": "+380991234567"}],
        "addresses": [],
        "confirm_duplicate_phones": True,
    }

    response2 = await http_client.post(
        url=BASE_URL, headers=headers, json=json2
    )

    assert response2.status_code == status.HTTP_201_CREATED
    assert response2.json() is not None


@pytest.mark.asyncio()
async def test_edit_client_with_duplicate_phone_returns_409(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3101
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    await setup_test_client(
        shop_id=shop_id,
        full_name="Перший Клієнт",
        phones=["+380509999999"],
    )

    client2_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Другий Клієнт",
        phones=["+380508888888"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"phones": [{"number": "+380509999999", "is_primary": True}]}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client2_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data["code"] == "duplicate_phones"
    assert data["duplicates"][0]["phone_number"] == "+380509999999"
    assert (
        data["duplicates"][0]["existing_clients"][0]["full_name"]
        == "Перший Клієнт"
    )


@pytest.mark.asyncio()
async def test_edit_client_with_duplicate_phone_confirmed(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3104
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    await setup_test_client(
        shop_id=shop_id,
        full_name="Перший Клієнт",
        phones=["+380509999999"],
    )

    client2_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Другий Клієнт",
        phones=["+380508888888"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "phones": [{"number": "+380509999999", "is_primary": True}],
        "confirm_duplicate_phones": True,
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client2_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
async def test_edit_client_keep_same_phone_numbers_integration(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3102
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501111111", "+380502222222"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    # First, get the client to obtain phone IDs
    get_response = await http_client.get(
        url=f"{BASE_URL}/{client_id}", headers=headers
    )
    assert get_response.status_code == status.HTTP_200_OK
    client_data = get_response.json()
    phone_ids = [phone["id"] for phone in client_data["phones"]]

    json = {
        "phones": [
            {
                "number": "+380501111111",
                "is_primary": True,
                "id": phone_ids[0],
            },
            {
                "number": "+380502222222",
                "is_primary": False,
                "id": phone_ids[1],
            },
        ]
    }

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone)
        .where(ClientPhone.client_id == client_id)
        .order_by(ClientPhone.id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 2
    assert phones[0].number == "+380501111111"
    assert phones[0].is_primary is True
    assert phones[1].number == "+380502222222"
    assert phones[1].is_primary is False


@pytest.mark.asyncio()
async def test_get_all_clients_filter_by_phone_no_duplicates(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2150
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт з багатьма телефонами",
        phones=[
            "+380501234567",
            "+380501234568",
            "+380501234569",
        ],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Інший Клієнт",
        phones=["+380509999999"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"phone": "50123456"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 1
    assert data[0]["full_name"] == "Клієнт з багатьма телефонами"


@pytest.mark.asyncio()
async def test_get_all_clients_pagination_no_duplicates_same_name(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2160
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for _i in range(10):
        await setup_test_client(
            shop_id=shop_id,
            full_name="Однакове Ім'я",
        )
    await session.commit()

    headers = customer_headers(telegram_id)

    all_client_ids: list[str] = []
    for offset in range(0, 10, 2):
        response = await http_client.get(
            url=f"{BASE_URL}/all",
            headers=headers,
            params={"limit": 2, "offset": offset},
        )
        assert response.status_code == status.HTTP_200_OK
        page_ids = [c["client_id"] for c in response.json()]
        all_client_ids.extend(page_ids)

    assert len(all_client_ids) == 10
    assert len(all_client_ids) == len(set(all_client_ids))


@pytest.mark.asyncio()
async def test_create_client_with_phone_normalization_leading_zero(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 4000
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Тест Нормалізації",
        "phones": [{"number": "0980074978"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone).where(
            ClientPhone.client_id == uuid.UUID(client_id)
        )
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380980074978"


@pytest.mark.asyncio()
async def test_create_client_with_phone_normalization_with_spaces(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 4001
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Тест Нормалізації з Пробілами",
        "phones": [{"number": "098 007 49 78"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone).where(
            ClientPhone.client_id == uuid.UUID(client_id)
        )
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380980074978"


@pytest.mark.asyncio()
async def test_create_client_with_phone_normalization_with_formatting(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 4002
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Тест Нормалізації з Форматуванням",
        "phones": [{"number": "+38(098)007-49-78"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone).where(
            ClientPhone.client_id == uuid.UUID(client_id)
        )
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380980074978"


@pytest.mark.asyncio()
async def test_create_client_with_invalid_phone_too_short(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 4003
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Тест Невалідного Номеру",
        "phones": [{"number": "098007497"}],
        "addresses": [],
    }

    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "phone" in response.json()["detail"].lower()


@pytest.mark.asyncio()
async def test_edit_client_with_phone_normalization(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 4004
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501111111"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"phones": [{"number": "0502222222", "is_primary": True}]}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    phone_result = await session.execute(
        select(ClientPhone).where(ClientPhone.client_id == client_id)
    )
    phones = phone_result.scalars().all()
    assert len(phones) == 1
    assert phones[0].number == "+380502222222"


@pytest.mark.asyncio()
async def test_edit_client_with_invalid_phone(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 4005
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501111111"],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"phones": [{"number": "123", "is_primary": True}]}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "phone" in response.json()["detail"].lower()


@pytest.mark.asyncio()
async def test_delete_client_unauthorized(
    http_client: AsyncClient,
) -> None:
    client_id = str(uuid.uuid4())
    response = await http_client.delete(url=f"{BASE_URL}/{client_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_client_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 1050
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    client_id = await setup_test_client(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{client_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_client_not_found_returns_ok(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1051
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


NOMINATIM_GEOCODE = "backend.infrastructure.nominatim.NominatimClient.geocode"


@pytest.mark.asyncio()
async def test_create_client_geocodes_address_when_shop_has_city(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1060
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, shop_city="Київ"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Геокод Клієнт",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
            }
        ],
    }

    fake_coords = CoordinatesDTO(latitude=50.45, longitude=30.52)

    with patch(
        NOMINATIM_GEOCODE,
        new_callable=AsyncMock,
        return_value=fake_coords,
    ) as mock_geocode:
        response = await http_client.post(
            url=BASE_URL, headers=headers, json=json
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_geocode.assert_called_once_with("Хрещатик", "10", "Київ")

    client_id = response.json()
    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addr = result.scalar_one()
    assert addr.latitude == 50.45
    assert addr.longitude == 30.52


@pytest.mark.asyncio()
async def test_create_client_skips_geocoding_when_coords_provided(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1061
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, shop_city="Київ"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Клієнт з Координатами",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
                "coordinates": {
                    "latitude": 50.4501,
                    "longitude": 30.5234,
                },
            }
        ],
    }

    with patch(
        NOMINATIM_GEOCODE,
        new_callable=AsyncMock,
    ) as mock_geocode:
        response = await http_client.post(
            url=BASE_URL, headers=headers, json=json
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_geocode.assert_not_called()

    client_id = response.json()
    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addr = result.scalar_one()
    assert addr.latitude == 50.4501
    assert addr.longitude == 30.5234


@pytest.mark.asyncio()
async def test_create_client_skips_geocoding_when_no_city(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1062
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {
        "full_name": "Клієнт без Міста",
        "phones": [{"number": "+380501234567"}],
        "addresses": [
            {
                "street": "Хрещатик",
                "house": "10",
            }
        ],
    }

    with patch(
        NOMINATIM_GEOCODE,
        new_callable=AsyncMock,
    ) as mock_geocode:
        response = await http_client.post(
            url=BASE_URL, headers=headers, json=json
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_geocode.assert_not_called()

    client_id = response.json()
    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(
            ClientAddress.client_id == uuid.UUID(client_id)
        )
    )
    addr = result.scalar_one()
    assert addr.latitude is None
    assert addr.longitude is None


@pytest.mark.asyncio()
async def test_edit_client_geocodes_new_address(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 1063
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, shop_city="Київ"
    )

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Клієнт",
        phones=["+380501234567"],
        addresses=[{"street": "Стара", "house": "1"}],
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    client_resp = await http_client.get(
        url=f"{BASE_URL}/{client_id}", headers=headers
    )
    client_data = client_resp.json()
    phone_id = client_data["phones"][0]["id"]

    fake_coords = CoordinatesDTO(latitude=50.46, longitude=30.53)

    json = {
        "phones": [
            {
                "number": "+380501234567",
                "is_primary": True,
                "id": phone_id,
            }
        ],
        "addresses": [
            {
                "street": "Нова вулиця",
                "house": "5",
                "is_primary": True,
            }
        ],
    }

    with patch(
        NOMINATIM_GEOCODE,
        new_callable=AsyncMock,
        return_value=fake_coords,
    ) as mock_geocode:
        response = await http_client.patch(
            url=f"{BASE_URL}/{client_id}",
            headers=headers,
            json=json,
        )

        assert response.status_code == status.HTTP_200_OK
        mock_geocode.assert_called_once_with("Нова вулиця", "5", "Київ")

    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = result.scalars().all()
    assert len(addresses) == 1
    assert addresses[0].latitude == 50.46
    assert addresses[0].longitude == 30.53
