import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import AddressType, ShopRole
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
                "address_type": AddressType.APARTMENT,
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
    assert addresses[0].address_type == AddressType.APARTMENT.value
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
                "address_type": AddressType.PRIVATE_HOUSE,
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
    assert addresses[0].address_type == AddressType.PRIVATE_HOUSE.value
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
                "address_type": AddressType.APARTMENT,
                "apartment": "10",
            },
            {
                "street": "Садова",
                "house": "22Б",
                "address_type": AddressType.PRIVATE_HOUSE,
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
