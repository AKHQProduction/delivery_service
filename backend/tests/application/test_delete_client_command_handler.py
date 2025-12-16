import uuid

import pytest

from backend.application.commands.delete_client import (
    DeleteClientCommand,
    DeleteClientCommandHandler,
)
from backend.application.errors import AccessDeniedError
from backend.application.interfaces.gateways.client_gateway import (
    CreateClientDTO,
)
from backend.application.vars import (
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
        if not user_id:
            user_id = UserId(uuid.uuid4())
        if not shop_id:
            shop_id = ShopId(uuid.uuid4())
        idp = InMemoryIdentityProvider(
            user_id=user_id, role=role, shop_id=shop_id
        )
        client_gateway = InMemoryClientGateway()
        tr_manager = FakeTransactionManager()

        handler = DeleteClientCommandHandler(
            idp=idp, client_gateway=client_gateway, tr_manager=tr_manager
        )

        return handler, idp, client_gateway, tr_manager

    return _make_handler


@pytest.mark.asyncio()
async def test_delete_product_success(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    client_id = ClientId(uuid.uuid4())
    await client_gateway.create_client(
        CreateClientDTO(
            client_id=client_id,
            shop_id=shop_id,
            full_name="Test Client",
            phones=[],
            addresses=[],
        )
    )

    command = DeleteClientCommand(client_id=client_id)

    await handler.handle(command)

    deleted_client = await client_gateway.load(client_id)
    assert deleted_client is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_access_denied_no_management_rights(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    client_id = ClientId(uuid.uuid4())
    await client_gateway.create_client(
        CreateClientDTO(
            client_id=client_id,
            shop_id=shop_id,
            full_name="Test Client",
            phones=[],
            addresses=[],
        )
    )

    command = DeleteClientCommand(client_id=client_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    deleted_client = await client_gateway.load(client_id)
    assert deleted_client is not None
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_client_id = ClientId(uuid.uuid4())

    command = DeleteClientCommand(client_id=non_existent_client_id)

    await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_access_denied_different_shop(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())

    handler, _, client_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    client_id = ClientId(uuid.uuid4())
    await client_gateway.create_client(
        CreateClientDTO(
            client_id=client_id,
            shop_id=other_shop_id,
            full_name="Test Client",
            phones=[],
            addresses=[],
        )
    )

    command = DeleteClientCommand(client_id=client_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    client = await client_gateway.load(client_id)
    assert client is not None
    assert not tr_manager.committed
