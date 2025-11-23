import uuid

import pytest

from backend.application.errors import (
    EntityNotFoundError,
    UserAlreadyRelatedToShopError,
)
from backend.application.usecases.invite_employee import AcceptInviteCommand
from backend.application.usecases.invite_employee.accept_invite import (
    AcceptInviteCommandHandler,
)
from backend.application.usecases.invite_employee.interfaces import Link
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryIdentityProvider,
    InMemoryLinkGateway,
    InMemoryShopGateway,
    InMemoryUserGateway,
)


@pytest.fixture()
def make_handler():
    def _make_handler(
        user_id: UserId | None = None,
        linked_users: set[UserId] | None = None,
    ):
        idp = InMemoryIdentityProvider(user_id=user_id)
        shop_gateway = InMemoryShopGateway(linked_users=linked_users)
        user_gateway = InMemoryUserGateway()
        link_gateway = InMemoryLinkGateway()
        tr_manager = FakeTransactionManager()

        handler = AcceptInviteCommandHandler(
            idp=idp,
            shop_gateway=shop_gateway,
            user_gateway=user_gateway,
            link_gateway=link_gateway,
            tr_manager=tr_manager,
        )

        return (
            handler,
            idp,
            shop_gateway,
            user_gateway,
            link_gateway,
            tr_manager,
        )

    return _make_handler


@pytest.mark.asyncio()
async def test_accept_invite_creates_new_user_when_no_current_user(
    make_handler,
) -> None:
    handler, _, shop_gateway, user_gateway, link_gateway, tr_manager = (
        make_handler()
    )

    shop_id = ShopId(uuid.uuid4())
    payload = "test_payload_123"
    link = Link(
        payload=payload,
        role=ShopRole.MANAGER,
        shop_id=shop_id,
        full_name="Manager Name",
    )
    await link_gateway.add(link)

    command = AcceptInviteCommand(
        payload=payload, tg_id=123456789, full_name="New User"
    )

    await handler.handle(command)

    # Check that a new user was created
    assert len(user_gateway.users) == 1
    created_user = next(iter(user_gateway.users.values()))
    assert created_user["tg_id"] == 123456789
    assert created_user["full_name"] == "New User"

    # Check that employee was added
    assert len(shop_gateway.employees) == 1
    employee = next(iter(shop_gateway.employees.values()))
    assert employee.shop_id == shop_id
    assert employee.role == ShopRole.MANAGER
    assert employee.full_name == "Manager Name"

    # Check that link was deleted
    assert len(link_gateway.links) == 0

    # Check that transaction was committed
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_accept_invite_uses_existing_user_when_current_user_exists(
    make_handler,
) -> None:
    existing_user_id = UserId(uuid.uuid4())
    handler, _, shop_gateway, user_gateway, link_gateway, tr_manager = (
        make_handler(user_id=existing_user_id)
    )

    shop_id = ShopId(uuid.uuid4())
    payload = "test_payload_456"
    link = Link(
        payload=payload,
        role=ShopRole.COURIER,
        shop_id=shop_id,
        full_name="Courier Name",
    )
    await link_gateway.add(link)

    command = AcceptInviteCommand(
        payload=payload, tg_id=987654321, full_name="Existing User"
    )

    await handler.handle(command)

    # Check that no new user was created
    assert len(user_gateway.users) == 0

    # Check that employee was added with existing user_id
    assert len(shop_gateway.employees) == 1
    employee = shop_gateway.employees[existing_user_id]
    assert employee.user_id == existing_user_id
    assert employee.shop_id == shop_id
    assert employee.role == ShopRole.COURIER
    assert employee.full_name == "Courier Name"

    # Check that link was deleted
    assert len(link_gateway.links) == 0

    # Check that transaction was committed
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_accept_invite_raises_error_when_link_not_found(
    make_handler,
) -> None:
    handler, *_ = make_handler()

    command = AcceptInviteCommand(
        payload="nonexistent_payload", tg_id=111222333, full_name="Test User"
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert "Invite link" in str(exc_info.value)


@pytest.mark.asyncio()
async def test_accept_invite_raises_error_when_user_already_related_to_shop(
    make_handler,
) -> None:
    existing_user_id = UserId(uuid.uuid4())
    handler, _, _, _, link_gateway, _ = make_handler(
        user_id=existing_user_id, linked_users={existing_user_id}
    )

    shop_id = ShopId(uuid.uuid4())
    payload = "test_payload_789"
    link = Link(
        payload=payload,
        role=ShopRole.MANAGER,
        shop_id=shop_id,
        full_name="Test Name",
    )
    await link_gateway.add(link)

    command = AcceptInviteCommand(
        payload=payload, tg_id=444555666, full_name="Test User"
    )

    with pytest.raises(UserAlreadyRelatedToShopError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_accept_invite_deletes_link_and_commits_transaction(
    make_handler,
) -> None:
    handler, _, _, _, link_gateway, tr_manager = make_handler()

    shop_id = ShopId(uuid.uuid4())
    payload = "test_payload_final"
    link = Link(
        payload=payload,
        role=ShopRole.MANAGER,
        shop_id=shop_id,
        full_name="Test Name",
    )
    await link_gateway.add(link)

    command = AcceptInviteCommand(
        payload=payload, tg_id=777888999, full_name="Final User"
    )

    await handler.handle(command)

    # Verify link was deleted
    remaining_link = await link_gateway.load_by_payload(payload)
    assert remaining_link is None

    # Verify transaction was committed
    assert tr_manager.committed is True
