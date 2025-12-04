import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    CreateClientDTO,
    PhoneDTO,
)
from backend.application.vars import AddressType, ClientId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)


@pytest.mark.asyncio()
async def test_create_client_saves_basic_data(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[],
        addresses=[],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one()

    assert client.id == client_id
    assert client.full_name == "Іван Іванов"
    assert client.shop_id == shop_id


@pytest.mark.asyncio()
async def test_create_client_with_single_phone_marks_it_primary(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[PhoneDTO(number="+380501234567")],
        addresses=[],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientPhone).where(ClientPhone.client_id == client_id)
    )
    phones = result.scalars().all()

    assert len(phones) == 1
    assert phones[0].number == "+380501234567"
    assert phones[0].is_primary is True


@pytest.mark.asyncio()
async def test_create_client_with_multiple_phones_marks_first_as_primary(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(number="+380501234567"),
            PhoneDTO(number="+380507654321"),
            PhoneDTO(number="+380509999999"),
        ],
        addresses=[],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientPhone)
        .where(ClientPhone.client_id == client_id)
        .order_by(ClientPhone.id)
    )
    phones = result.scalars().all()

    assert len(phones) == 3
    assert phones[0].number == "+380501234567"
    assert phones[0].is_primary is True
    assert phones[1].number == "+380507654321"
    assert phones[1].is_primary is False
    assert phones[2].number == "+380509999999"
    assert phones[2].is_primary is False


@pytest.mark.asyncio()
async def test_create_client_with_single_address_marks_it_primary(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[],
        addresses=[
            AddressDTO(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                entrance="1",
                floor="2",
                intercom="5",
            )
        ],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = result.scalars().all()

    assert len(addresses) == 1
    assert addresses[0].street == "Хрещатик"
    assert addresses[0].house == "10"
    assert addresses[0].address_type == AddressType.APARTMENT.value
    assert addresses[0].apartment == "5"
    assert addresses[0].entrance == "1"
    assert addresses[0].floor == "2"
    assert addresses[0].intercom == "5"
    assert addresses[0].is_primary is True


@pytest.mark.asyncio()
async def test_create_client_with_multiple_addresses_marks_first_as_primary(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[],
        addresses=[
            AddressDTO(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
            ),
            AddressDTO(
                street="Шевченка",
                house="20",
                address_type=AddressType.PRIVATE_HOUSE,
            ),
            AddressDTO(
                street="Грушевського",
                house="30",
                address_type=AddressType.APARTMENT,
                apartment="15",
            ),
        ],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientAddress)
        .where(ClientAddress.client_id == client_id)
        .order_by(ClientAddress.id)
    )
    addresses = result.scalars().all()

    assert len(addresses) == 3
    assert addresses[0].street == "Хрещатик"
    assert addresses[0].is_primary is True
    assert addresses[1].street == "Шевченка"
    assert addresses[1].is_primary is False
    assert addresses[2].street == "Грушевського"
    assert addresses[2].is_primary is False


@pytest.mark.asyncio()
async def test_create_client_with_private_house_address(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[],
        addresses=[
            AddressDTO(
                street="Заміська",
                house="15А",
                address_type=AddressType.PRIVATE_HOUSE,
            )
        ],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientAddress).where(ClientAddress.client_id == client_id)
    )
    addresses = result.scalars().all()

    assert len(addresses) == 1
    assert addresses[0].street == "Заміська"
    assert addresses[0].house == "15А"
    assert addresses[0].address_type == AddressType.PRIVATE_HOUSE.value
    assert addresses[0].apartment is None
    assert addresses[0].entrance is None
    assert addresses[0].floor is None
    assert addresses[0].intercom is None


@pytest.mark.asyncio()
async def test_create_client_with_phones_and_addresses(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(number="+380501234567"),
            PhoneDTO(number="+380507654321"),
        ],
        addresses=[
            AddressDTO(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
            ),
            AddressDTO(
                street="Шевченка",
                house="20",
                address_type=AddressType.PRIVATE_HOUSE,
            ),
        ],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    # Проверяем клиента
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one()
    assert client.full_name == "Іван Іванов"

    # Проверяем телефоны
    phones_result = await session.execute(
        select(ClientPhone)
        .where(ClientPhone.client_id == client_id)
        .order_by(ClientPhone.id)
    )
    phones = phones_result.scalars().all()
    assert len(phones) == 2
    assert phones[0].is_primary is True
    assert phones[1].is_primary is False

    # Проверяем адреса
    addresses_result = await session.execute(
        select(ClientAddress)
        .where(ClientAddress.client_id == client_id)
        .order_by(ClientAddress.id)
    )
    addresses = addresses_result.scalars().all()
    assert len(addresses) == 2
    assert addresses[0].is_primary is True
    assert addresses[1].is_primary is False


def test_next_id_returns_uuid_v7(
    client_gateway: SQLAlchemyClientGateway,
) -> None:
    result = client_gateway.next_id()

    assert isinstance(result, uuid.UUID)
    assert result.version == 7


def test_next_id_returns_unique_ids(
    client_gateway: SQLAlchemyClientGateway,
) -> None:
    id1 = client_gateway.next_id()
    id2 = client_gateway.next_id()
    id3 = client_gateway.next_id()

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3
    assert all(
        isinstance(client_id, uuid.UUID) for client_id in [id1, id2, id3]
    )


@pytest.mark.asyncio()
async def test_phone_numbers_linked_to_shop(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = ClientId(uuid.uuid4())
    await session.flush()

    dto = CreateClientDTO(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[PhoneDTO(number="+380501234567")],
        addresses=[],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await session.execute(
        select(ClientPhone).where(ClientPhone.client_id == client_id)
    )
    phone = result.scalar_one()

    assert phone.shop_id == shop_id
