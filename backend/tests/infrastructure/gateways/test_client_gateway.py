import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    CreateClientDTO,
    GetClientsFilters,
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


@pytest.mark.asyncio()
async def test_read_returns_client_with_all_data(
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
        full_name="Марія Марченко",
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
                entrance="1",
                floor="2",
                intercom="5",
            ),
            AddressDTO(
                street="Шевченка",
                house="20",
                address_type=AddressType.PRIVATE_HOUSE,
            ),
        ],
        custom_id="CLIENT-001",
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await client_gateway.read(client_id)

    assert result is not None
    assert result.client_id == client_id
    assert result.full_name == "Марія Марченко"
    assert result.custom_id == "CLIENT-001"

    assert len(result.phones) == 2
    assert result.phones[0].number == "+380501234567"
    assert result.phones[0].is_primary is True
    assert result.phones[1].number == "+380507654321"
    assert result.phones[1].is_primary is False

    assert len(result.addresses) == 2
    assert result.addresses[0].street == "Хрещатик"
    assert result.addresses[0].house == "10"
    assert result.addresses[0].address_type == AddressType.APARTMENT
    assert result.addresses[0].apartment == "5"
    assert result.addresses[0].is_primary is True
    assert result.addresses[1].street == "Шевченка"
    assert result.addresses[1].house == "20"
    assert result.addresses[1].address_type == AddressType.PRIVATE_HOUSE
    assert result.addresses[1].is_primary is False


@pytest.mark.asyncio()
async def test_read_returns_none_when_client_not_found(
    client_gateway: SQLAlchemyClientGateway,
) -> None:
    non_existent_id = ClientId(uuid.uuid4())

    result = await client_gateway.read(non_existent_id)

    assert result is None


@pytest.mark.asyncio()
async def test_read_client_without_phones_and_addresses(
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
        full_name="Олексій Олексієнко",
        phones=[],
        addresses=[],
    )

    await client_gateway.create_client(dto)
    await session.flush()

    result = await client_gateway.read(client_id)

    assert result is not None
    assert result.client_id == client_id
    assert result.full_name == "Олексій Олексієнко"
    assert result.phones == []
    assert result.addresses == []
    assert result.custom_id is None


@pytest.mark.asyncio()
async def test_read_all_returns_all_clients_for_shop(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    # Create three clients
    client_id_1 = ClientId(uuid.uuid4())
    dto_1 = CreateClientDTO(
        client_id=client_id_1,
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=[PhoneDTO(number="+380501111111")],
        addresses=[],
    )
    await client_gateway.create_client(dto_1)

    client_id_2 = ClientId(uuid.uuid4())
    dto_2 = CreateClientDTO(
        client_id=client_id_2,
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=[PhoneDTO(number="+380502222222")],
        addresses=[],
    )
    await client_gateway.create_client(dto_2)

    client_id_3 = ClientId(uuid.uuid4())
    dto_3 = CreateClientDTO(
        client_id=client_id_3,
        shop_id=shop_id,
        full_name="Віктор Вікторенко",
        phones=[PhoneDTO(number="+380503333333")],
        addresses=[],
    )
    await client_gateway.create_client(dto_3)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id)
    pagination = Pagination(offset=0, limit=100, order=SortOrder.ASC)

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 3
    assert result[0].full_name == "Анна Антоненко"
    assert result[1].full_name == "Борис Борисенко"
    assert result[2].full_name == "Віктор Вікторенко"


@pytest.mark.asyncio()
async def test_read_all_filters_by_full_name(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    client_id_1 = ClientId(uuid.uuid4())
    dto_1 = CreateClientDTO(
        client_id=client_id_1,
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=[],
        addresses=[],
    )
    await client_gateway.create_client(dto_1)

    client_id_2 = ClientId(uuid.uuid4())
    dto_2 = CreateClientDTO(
        client_id=client_id_2,
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=[],
        addresses=[],
    )
    await client_gateway.create_client(dto_2)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id, full_name="Анна")
    pagination = Pagination()

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 1
    assert result[0].full_name == "Анна Антоненко"


@pytest.mark.asyncio()
async def test_read_all_filters_by_phone_number(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    client_id_1 = ClientId(uuid.uuid4())
    dto_1 = CreateClientDTO(
        client_id=client_id_1,
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=[PhoneDTO(number="+380501111111")],
        addresses=[],
    )
    await client_gateway.create_client(dto_1)

    client_id_2 = ClientId(uuid.uuid4())
    dto_2 = CreateClientDTO(
        client_id=client_id_2,
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=[PhoneDTO(number="+380502222222")],
        addresses=[],
    )
    await client_gateway.create_client(dto_2)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id, phone="1111")
    pagination = Pagination()

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 1
    assert result[0].full_name == "Анна Антоненко"


@pytest.mark.asyncio()
async def test_read_all_filters_by_custom_id(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    client_id_1 = ClientId(uuid.uuid4())
    dto_1 = CreateClientDTO(
        client_id=client_id_1,
        shop_id=shop_id,
        full_name="Анна Антоненко",
        phones=[],
        addresses=[],
        custom_id="VIP-001",
    )
    await client_gateway.create_client(dto_1)

    client_id_2 = ClientId(uuid.uuid4())
    dto_2 = CreateClientDTO(
        client_id=client_id_2,
        shop_id=shop_id,
        full_name="Борис Борисенко",
        phones=[],
        addresses=[],
        custom_id="VIP-002",
    )
    await client_gateway.create_client(dto_2)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id, custom_id="VIP-001")
    pagination = Pagination()

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 1
    assert result[0].full_name == "Анна Антоненко"
    assert result[0].custom_id == "VIP-001"


@pytest.mark.asyncio()
async def test_read_all_applies_pagination_limit(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    for i in range(5):
        client_id = ClientId(uuid.uuid4())
        dto = CreateClientDTO(
            client_id=client_id,
            shop_id=shop_id,
            full_name=f"Client {i}",
            phones=[],
            addresses=[],
        )
        await client_gateway.create_client(dto)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id)
    pagination = Pagination(offset=0, limit=3)

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 3


@pytest.mark.asyncio()
async def test_read_all_applies_pagination_offset(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    for i in range(5):
        client_id = ClientId(uuid.uuid4())
        dto = CreateClientDTO(
            client_id=client_id,
            shop_id=shop_id,
            full_name=f"Client {i:02d}",
            phones=[],
            addresses=[],
        )
        await client_gateway.create_client(dto)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id)
    pagination = Pagination(offset=2, limit=2, order=SortOrder.ASC)

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 2
    assert result[0].full_name == "Client 02"
    assert result[1].full_name == "Client 03"


@pytest.mark.asyncio()
async def test_read_all_sorts_by_full_name_descending(
    session: AsyncSession,
    client_gateway: SQLAlchemyClientGateway,
    create_shop,
) -> None:
    shop_id = await create_shop()
    await session.flush()

    client_id_1 = ClientId(uuid.uuid4())
    dto_1 = CreateClientDTO(
        client_id=client_id_1,
        shop_id=shop_id,
        full_name="Анна",
        phones=[],
        addresses=[],
    )
    await client_gateway.create_client(dto_1)

    client_id_2 = ClientId(uuid.uuid4())
    dto_2 = CreateClientDTO(
        client_id=client_id_2,
        shop_id=shop_id,
        full_name="Борис",
        phones=[],
        addresses=[],
    )
    await client_gateway.create_client(dto_2)

    client_id_3 = ClientId(uuid.uuid4())
    dto_3 = CreateClientDTO(
        client_id=client_id_3,
        shop_id=shop_id,
        full_name="Віктор",
        phones=[],
        addresses=[],
    )
    await client_gateway.create_client(dto_3)

    await session.flush()

    filters = GetClientsFilters(shop_id=shop_id)
    pagination = Pagination(order=SortOrder.DESC)

    result = await client_gateway.read_all(filters, pagination)

    assert len(result) == 3
    assert result[0].full_name == "Віктор"
    assert result[1].full_name == "Борис"
    assert result[2].full_name == "Анна"


@pytest.mark.asyncio()
async def test_delete_client(
    client_gateway: SQLAlchemyClientGateway,
    session: AsyncSession,
    setup_test_client,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    await session.flush()

    client_before = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    assert client_before.scalar_one() is not None

    await client_gateway.delete(client_id)
    await session.flush()

    client_after = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    assert client_after.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_delete_product_not_exists(
    client_gateway: SQLAlchemyClientGateway,
    session: AsyncSession,
) -> None:
    non_existent_product_id = ClientId(uuid.uuid4())

    await client_gateway.delete(non_existent_product_id)
    await session.flush()


@pytest.mark.asyncio()
async def test_load_product(
    client_gateway: SQLAlchemyClientGateway,
    session: AsyncSession,
    setup_test_client,
    create_shop,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    await session.flush()

    client = await client_gateway.load(client_id)

    assert client is not None
    assert client.client_id == client_id
    assert client.shop_id == shop_id
    assert client.full_name == "Test Client"


@pytest.mark.asyncio()
async def test_load_product_returns_none_when_not_exists(
    client_gateway: SQLAlchemyClientGateway,
) -> None:
    client_id = ClientId(uuid.uuid4())

    client = await client_gateway.load(client_id)

    assert client is None
