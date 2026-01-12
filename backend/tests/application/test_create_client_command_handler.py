import uuid

import pytest

from backend.application.commands.create_client import (
    Address,
    CreateClientCommand,
    CreateClientCommandHandler,
    Phone,
)
from backend.application.errors import (
    AccessDeniedError,
    AuthorizationError,
)
from backend.application.vars import AddressType, ShopId, ShopRole, UserId
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryClientGateway,
    InMemoryIdentityProvider,
)


@pytest.fixture()
def make_handler():
    def _make_handler(
        user_id: UserId | None = None,
        shop_id: ShopId | None = None,
        role: ShopRole = ShopRole.OWNER,
    ):
        identity_provider = InMemoryIdentityProvider(
            user_id=user_id, shop_id=shop_id, role=role
        )
        client_gateway = InMemoryClientGateway()
        tr_manager = FakeTransactionManager()

        handler = CreateClientCommandHandler(
            idp=identity_provider,
            client_gateway=client_gateway,
            tr_manager=tr_manager,
        )

        return handler, client_gateway, identity_provider, tr_manager

    return _make_handler


@pytest.fixture()
def command() -> CreateClientCommand:
    return CreateClientCommand(
        full_name="Іван Іванов",
        phones=[Phone(number="+380501234567")],
        addresses=[
            Address(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
            )
        ],
    )


@pytest.mark.asyncio()
async def test_create_client_successfully(make_handler, command) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    client_id = await handler.handle(command)

    assert len(client_gateway.clients) == 1
    assert client_id in client_gateway.clients
    assert tr_manager.committed is True

    created_client = client_gateway.clients[client_id]
    assert created_client.full_name == "Іван Іванов"
    assert created_client.shop_id == shop_id
    assert len(created_client.phones) == 1
    assert created_client.phones[0].number == "+380501234567"
    assert len(created_client.addresses) == 1
    assert created_client.addresses[0].street == "Хрещатик"


@pytest.mark.asyncio()
async def test_create_client_with_multiple_phones_and_addresses(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    command = CreateClientCommand(
        full_name="Петро Петренко",
        phones=[
            Phone(number="+380501234567"),
            Phone(number="+380507654321"),
        ],
        addresses=[
            Address(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
            ),
            Address(
                street="Шевченка",
                house="20",
                address_type=AddressType.PRIVATE_HOUSE,
            ),
        ],
    )

    client_id = await handler.handle(command)

    created_client = client_gateway.clients[client_id]
    assert len(created_client.phones) == 2
    assert len(created_client.addresses) == 2


@pytest.mark.asyncio()
async def test_raise_authorization_error_when_user_not_authorized(
    make_handler, command
) -> None:
    handler, _, _, _ = make_handler()

    with pytest.raises(AuthorizationError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_access_denied_when_user_is_courier(
    make_handler, command
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_owner_can_create_client(make_handler, command) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    client_id = await handler.handle(command)

    assert len(client_gateway.clients) == 1
    assert client_id in client_gateway.clients


@pytest.mark.asyncio()
async def test_manager_can_create_client(make_handler, command) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.MANAGER
    )

    client_id = await handler.handle(command)

    assert len(client_gateway.clients) == 1
    assert client_id in client_gateway.clients


@pytest.mark.asyncio()
async def test_create_client_with_custom_id(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    command = CreateClientCommand(
        full_name="Марія Марченко",
        phones=[Phone(number="+380501234567")],
        addresses=[
            Address(
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
            )
        ],
        custom_id="CUSTOM-123",
    )

    client_id = await handler.handle(command)

    created_client = client_gateway.clients[client_id]
    assert created_client.custom_id == "CUSTOM-123"


@pytest.mark.asyncio()
async def test_create_client_with_no_phones_and_addresses(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    command = CreateClientCommand(
        full_name="Олексій Олексієнко",
        phones=[],
        addresses=[],
    )

    client_id = await handler.handle(command)

    created_client = client_gateway.clients[client_id]
    assert created_client.full_name == "Олексій Олексієнко"
    assert len(created_client.phones) == 0
    assert len(created_client.addresses) == 0


@pytest.mark.asyncio()
async def test_create_client_returns_unique_client_id(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _ = make_handler(user_id=user_id, shop_id=shop_id)

    command1 = CreateClientCommand(
        full_name="Перший Клієнт",
        phones=[Phone(number="+380501111111")],
    )
    command2 = CreateClientCommand(
        full_name="Другий Клієнт",
        phones=[Phone(number="+380502222222")],
    )

    client_id_1 = await handler.handle(command1)
    client_id_2 = await handler.handle(command2)

    assert client_id_1 != client_id_2


@pytest.mark.asyncio()
async def test_create_client_with_private_house_address(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    command = CreateClientCommand(
        full_name="Сергій Сергієнко",
        phones=[Phone(number="+380501234567")],
        addresses=[
            Address(
                street="Заміська",
                house="15А",
                address_type=AddressType.PRIVATE_HOUSE,
            )
        ],
    )

    client_id = await handler.handle(command)

    created_client = client_gateway.clients[client_id]
    assert (
        created_client.addresses[0].address_type == AddressType.PRIVATE_HOUSE
    )
    assert created_client.addresses[0].apartment is None
