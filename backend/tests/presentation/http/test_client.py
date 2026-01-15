import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        "custom_id": "ABCD",
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
    assert client.custom_id == "ABCD"

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
        "custom_id": "HOUSE-001",
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
        custom_id="TEST-001",
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
    assert data["custom_id"] == "TEST-001"
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
        custom_id="VIP-001",
        phones=["+380501111111"],
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Борис Борисенко",
        custom_id="VIP-002",
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
async def test_get_all_clients_filter_by_custom_id(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 2103
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    # Create clients directly in DB
    await setup_test_client(
        shop_id=shop_id,
        full_name="Анна Антоненко",
        custom_id="VIP-001",
    )
    await setup_test_client(
        shop_id=shop_id,
        full_name="Борис Борисенко",
        custom_id="VIP-002",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    # Filter by custom_id
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"custom_id": "VIP-001"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Анна Антоненко"
    assert data[0]["custom_id"] == "VIP-001"


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

    assert response.status_code == status.HTTP_200_OK
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
        custom_id="ORIG-001",
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
    assert client.custom_id == "ORIG-001"


@pytest.mark.asyncio()
async def test_edit_client_custom_id(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
) -> None:
    telegram_id = 3001
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Ім'я Клієнта",
        custom_id="OLD-ID",
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"custom_id": "NEW-ID-123"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}", headers=headers, json=json
    )

    assert response.status_code == status.HTTP_200_OK

    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one()
    assert client.custom_id == "NEW-ID-123"
    assert client.full_name == "Ім'я Клієнта"


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
        custom_id="OLD-ID",
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
        "custom_id": "ALL-NEW-999",
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
    assert client.custom_id == "ALL-NEW-999"

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
async def test_create_client_with_duplicate_phone_number_allowed(
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
        "phones": [{"number": "+380991234567"}],  # Same phone - allowed
        "addresses": [],
    }

    response2 = await http_client.post(
        url=BASE_URL, headers=headers, json=json2
    )

    assert response2.status_code == status.HTTP_201_CREATED
    assert response2.json() is not None  # Returns ClientId (UUID)


@pytest.mark.asyncio()
async def test_edit_client_with_duplicate_phone_number_allowed(
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

    json = {
        "phones": [{"number": "+380509999999", "is_primary": True}]
    }  # Same as client1 - allowed

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
