import uuid

import pytest

from backend.application.commands import (
    CreateNewShopCommand,
    CreateNewShopCommandHandler,
)
from backend.application.errors import (
    AuthorizationError,
    UserAlreadyRelatedToShopError,
)
from backend.application.vars import UserId
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryIdentityProvider,
    InMemoryShopGateway,
)


@pytest.fixture()
def make_handler():
    def _make_handler(
        user_id: UserId | None = None, related_user: set[UserId] | None = None
    ):
        identity_provider = InMemoryIdentityProvider(user_id=user_id)
        shop_gateway = InMemoryShopGateway(linked_users=related_user)
        tr_manager = FakeTransactionManager()

        handler = CreateNewShopCommandHandler(
            shop_gateway=shop_gateway,
            identity_provider=identity_provider,
            tr_manager=tr_manager,
        )

        return handler, shop_gateway, identity_provider, tr_manager

    return _make_handler


@pytest.fixture()
def command() -> CreateNewShopCommand:
    return CreateNewShopCommand(name="NewShop")


@pytest.mark.asyncio()
async def test_create_new_shop_if_not_exists(make_handler, command) -> None:
    user_id = UserId(uuid.uuid4())
    handler, shop_gateway, _, tr_manager = make_handler(user_id=user_id)

    await handler.handle(command)

    assert len(shop_gateway.shops) == 1
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_raise_authorization_error_when_user_not_exists(
    make_handler, command
) -> None:
    handler, _, _, _ = make_handler()

    with pytest.raises(AuthorizationError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_error_when_user_relate_to_another_shop(
    make_handler, command
) -> None:
    user_id = UserId(uuid.uuid4())

    handler, _, _, _ = make_handler(user_id=user_id, related_user={user_id})

    with pytest.raises(UserAlreadyRelatedToShopError):
        await handler.handle(command)
