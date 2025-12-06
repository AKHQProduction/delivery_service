import uuid

import pytest

from backend.application.commands.edit_client import (
    Address,
    EditClientCommand,
    EditClientCommandHandler,
    Phone,
)
from backend.application.errors import (
    AccessDeniedError,
    AuthorizationError,
    EntityNotFoundError,
    InvalidPrimaryFlagError,
    PhoneNumberAlreadyExistsError,
)
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    ClientDM,
    PhoneDTO,
)
from backend.application.vars import (
    AddressType,
    ClientId,
    ShopId,
    ShopRole,
    UserId,
)
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

        handler = EditClientCommandHandler(
            idp=identity_provider,
            client_gateway=client_gateway,
            tr_manager=tr_manager,
        )

        return handler, client_gateway, identity_provider, tr_manager

    return _make_handler


def setup_client_in_gateway(
    client_gateway: InMemoryClientGateway, shop_id: ShopId
) -> ClientId:
    client_id = ClientId(uuid.uuid4())
    client = ClientDM(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Original Name",
        custom_id="ORIG-001",
        phones=[
            PhoneDTO(number="+380501111111", is_primary=True),
            PhoneDTO(number="+380502222222", is_primary=False),
        ],
        addresses=[
            AddressDTO(
                street="Original Street",
                house="1",
                address_type=AddressType.APARTMENT,
                apartment="10",
                is_primary=True,
            )
        ],
    )
    client_gateway.clients[client_id] = client
    return client_id


@pytest.mark.asyncio()
async def test_edit_client_full_name(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        full_name="Updated Name",
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert updated_client.full_name == "Updated Name"
    assert updated_client.custom_id == "ORIG-001"
    assert tr_manager.committed is True


@pytest.mark.asyncio()
async def test_edit_client_custom_id(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        custom_id="NEW-002",
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert updated_client.custom_id == "NEW-002"
    assert updated_client.full_name == "Original Name"


@pytest.mark.asyncio()
async def test_edit_client_phones(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(number="+380509999999", is_primary=True),
            Phone(number="+380508888888", is_primary=False),
            Phone(number="+380507777777", is_primary=False),
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 3
    assert updated_client.phones[0].number == "+380509999999"
    assert updated_client.phones[0].is_primary is True
    assert updated_client.phones[1].number == "+380508888888"
    assert updated_client.phones[1].is_primary is False
    assert updated_client.phones[2].number == "+380507777777"
    assert updated_client.phones[2].is_primary is False


@pytest.mark.asyncio()
async def test_edit_client_addresses(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        addresses=[
            Address(
                street="New Street",
                house="100",
                address_type=AddressType.PRIVATE_HOUSE,
                is_primary=True,
            ),
            Address(
                street="Another Street",
                house="200",
                address_type=AddressType.APARTMENT,
                apartment="50",
                is_primary=False,
            ),
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.addresses) == 2
    assert updated_client.addresses[0].street == "New Street"
    assert updated_client.addresses[0].house == "100"
    assert (
        updated_client.addresses[0].address_type == AddressType.PRIVATE_HOUSE
    )
    assert updated_client.addresses[0].is_primary is True
    assert updated_client.addresses[1].street == "Another Street"
    assert updated_client.addresses[1].is_primary is False


@pytest.mark.asyncio()
async def test_edit_client_all_fields(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        full_name="Completely New Name",
        custom_id="ALL-NEW-003",
        phones=[Phone(number="+380501234567", is_primary=True)],
        addresses=[
            Address(
                street="Brand New Street",
                house="999",
                address_type=AddressType.APARTMENT,
                apartment="1",
                is_primary=True,
            )
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert updated_client.full_name == "Completely New Name"
    assert updated_client.custom_id == "ALL-NEW-003"
    assert len(updated_client.phones) == 1
    assert updated_client.phones[0].number == "+380501234567"
    assert len(updated_client.addresses) == 1
    assert updated_client.addresses[0].street == "Brand New Street"


@pytest.mark.asyncio()
async def test_edit_client_clear_phones(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        phones=[],  # Clear all phones
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 0


@pytest.mark.asyncio()
async def test_edit_client_clear_addresses(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        addresses=[],  # Clear all addresses
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.addresses) == 0


@pytest.mark.asyncio()
async def test_edit_client_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _ = make_handler(user_id=user_id, shop_id=shop_id)

    non_existent_client_id = ClientId(uuid.uuid4())

    command = EditClientCommand(
        client_id=non_existent_client_id,
        full_name="New Name",
    )

    with pytest.raises(EntityNotFoundError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_edit_client_unauthorized(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    _, client_gateway, _, _ = make_handler(user_id=user_id, shop_id=shop_id)
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    handler, _, _, _ = make_handler()

    command = EditClientCommand(
        client_id=client_id,
        full_name="New Name",
    )

    with pytest.raises(AuthorizationError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_edit_client_access_denied_courier(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    _, client_gateway, _, _ = make_handler(user_id=user_id, shop_id=shop_id)
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    handler, _, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    command = EditClientCommand(
        client_id=client_id,
        full_name="New Name",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_edit_client_access_denied_different_shop(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    _, client_gateway, _, _ = make_handler(user_id=user_id, shop_id=shop_id)
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    different_shop_id = ShopId(uuid.uuid4())
    identity_provider = InMemoryIdentityProvider(
        user_id=user_id, shop_id=different_shop_id, role=ShopRole.OWNER
    )
    tr_manager = FakeTransactionManager()
    handler = EditClientCommandHandler(
        idp=identity_provider,
        client_gateway=client_gateway,
        tr_manager=tr_manager,
    )

    command = EditClientCommand(
        client_id=client_id,
        full_name="New Name",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_owner_can_edit_client(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        full_name="Owner Updated",
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert updated_client.full_name == "Owner Updated"


@pytest.mark.asyncio()
async def test_manager_can_edit_client(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.MANAGER
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        full_name="Manager Updated",
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert updated_client.full_name == "Manager Updated"


@pytest.mark.asyncio()
async def test_edit_client_with_duplicate_phone_number(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )

    client1_id = ClientId(uuid.uuid4())
    client1 = ClientDM(
        client_id=client1_id,
        shop_id=shop_id,
        full_name="First Client",
        phones=[PhoneDTO(number="+380509999999", is_primary=True)],
        addresses=[],
    )
    client_gateway.clients[client1_id] = client1

    client2_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client2_id,
        phones=[
            Phone(number="+380509999999", is_primary=True)
        ],  # Same as client1!
    )

    with pytest.raises(PhoneNumberAlreadyExistsError) as exc_info:
        await handler.handle(command)

    assert "+380509999999" in str(exc_info.value.message)


@pytest.mark.asyncio()
async def test_edit_client_keep_same_phone_numbers(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(number="+380501111111", is_primary=True),  # Original phone
            Phone(number="+380502222222", is_primary=False),  # Original phone
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 2
    assert updated_client.phones[0].number == "+380501111111"
    assert updated_client.phones[1].number == "+380502222222"


@pytest.mark.asyncio()
async def test_edit_client_partially_update_phones(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(
                number="+380501111111", is_primary=True
            ),  # Keep this old phone
            Phone(number="+380509999999", is_primary=False),  # Add new phone
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 2
    assert updated_client.phones[0].number == "+380501111111"
    assert updated_client.phones[1].number == "+380509999999"


def test_edit_command_raises_error_when_no_primary_phone() -> None:
    client_id = ClientId(uuid.uuid4())

    with pytest.raises(InvalidPrimaryFlagError) as exc_info:
        EditClientCommand(
            client_id=client_id,
            phones=[
                Phone(number="+380501234567", is_primary=False),
                Phone(number="+380507654321", is_primary=False),
            ],
        )

    assert "phone" in exc_info.value.message.lower()


def test_edit_command_raises_error_when_multiple_primary_phones() -> None:
    client_id = ClientId(uuid.uuid4())

    with pytest.raises(InvalidPrimaryFlagError) as exc_info:
        EditClientCommand(
            client_id=client_id,
            phones=[
                Phone(number="+380501234567", is_primary=True),
                Phone(number="+380507654321", is_primary=True),
            ],
        )

    assert "phone" in exc_info.value.message.lower()
    assert "2" in exc_info.value.message


def test_edit_command_raises_error_when_no_primary_address() -> None:
    client_id = ClientId(uuid.uuid4())

    with pytest.raises(InvalidPrimaryFlagError) as exc_info:
        EditClientCommand(
            client_id=client_id,
            addresses=[
                Address(
                    street="Street 1",
                    house="1",
                    address_type=AddressType.APARTMENT,
                    is_primary=False,
                ),
                Address(
                    street="Street 2",
                    house="2",
                    address_type=AddressType.APARTMENT,
                    is_primary=False,
                ),
            ],
        )

    assert "address" in exc_info.value.message.lower()


def test_edit_command_raises_error_when_multiple_primary_addresses() -> None:
    client_id = ClientId(uuid.uuid4())

    with pytest.raises(InvalidPrimaryFlagError) as exc_info:
        EditClientCommand(
            client_id=client_id,
            addresses=[
                Address(
                    street="Street 1",
                    house="1",
                    address_type=AddressType.APARTMENT,
                    is_primary=True,
                ),
                Address(
                    street="Street 2",
                    house="2",
                    address_type=AddressType.APARTMENT,
                    is_primary=True,
                ),
            ],
        )

    assert "address" in exc_info.value.message.lower()
    assert "2" in exc_info.value.message


def test_edit_command_succeeds_with_exactly_one_primary_phone() -> None:
    client_id = ClientId(uuid.uuid4())

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(number="+380501234567", is_primary=True),
            Phone(number="+380507654321", is_primary=False),
        ],
    )

    assert command.phones is not None
    assert len(command.phones) == 2


def test_edit_command_succeeds_with_exactly_one_primary_address() -> None:
    client_id = ClientId(uuid.uuid4())

    command = EditClientCommand(
        client_id=client_id,
        addresses=[
            Address(
                street="Street 1",
                house="1",
                address_type=AddressType.APARTMENT,
                is_primary=True,
            ),
            Address(
                street="Street 2",
                house="2",
                address_type=AddressType.APARTMENT,
                is_primary=False,
            ),
        ],
    )

    assert command.addresses is not None
    assert len(command.addresses) == 2


@pytest.mark.asyncio()
async def test_smart_update_phone_update_existing(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    # Get original phone IDs
    original_client = client_gateway.clients[client_id]
    original_phone_id = original_client.phones[0].id

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(
                number="+380509999999",  # Changed number
                is_primary=True,
                id=original_phone_id,  # Same ID
            )
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 1
    assert updated_client.phones[0].number == "+380509999999"
    assert updated_client.phones[0].id == original_phone_id  # ID not changed


@pytest.mark.asyncio()
async def test_smart_update_phone_add_new(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    # Keep existing phone + add new one
    original_client = client_gateway.clients[client_id]
    original_phone_id = original_client.phones[0].id

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(
                number="+380501111111",
                is_primary=True,
                id=original_phone_id,
            ),  # Keep existing
            Phone(number="+380509999999", is_primary=False),  # Add new
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 2
    assert updated_client.phones[0].number == "+380501111111"
    assert updated_client.phones[1].number == "+380509999999"


@pytest.mark.asyncio()
async def test_smart_update_phone_remove(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    # Only send first phone, second should be deleted
    original_client = client_gateway.clients[client_id]
    first_phone_id = original_client.phones[0].id

    command = EditClientCommand(
        client_id=client_id,
        phones=[
            Phone(
                number="+380501111111",
                is_primary=True,
                id=first_phone_id,
            )  # Only keep first
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.phones) == 1
    assert updated_client.phones[0].number == "+380501111111"


@pytest.mark.asyncio()
async def test_smart_update_address_update_existing(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, client_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id
    )
    client_id = setup_client_in_gateway(client_gateway, shop_id)

    # Get original address ID
    original_client = client_gateway.clients[client_id]
    original_address_id = original_client.addresses[0].id

    command = EditClientCommand(
        client_id=client_id,
        addresses=[
            Address(
                street="New Street",  # Changed
                house="100",  # Changed
                address_type=AddressType.PRIVATE_HOUSE,  # Changed
                is_primary=True,
                id=original_address_id,  # Same ID
            )
        ],
    )

    await handler.handle(command)

    updated_client = client_gateway.clients[client_id]
    assert len(updated_client.addresses) == 1
    assert updated_client.addresses[0].street == "New Street"
    assert updated_client.addresses[0].id == original_address_id
