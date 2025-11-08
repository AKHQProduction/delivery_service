import uuid

import pytest

from backend.application.commands import (
    BotStartCommand,
    BotStartCommandHandler,
)
from backend.application.vars import UserId
from backend.infrastructure.in_memory import (
    InMemoryIdentityProvider,
    InMemoryShopGateway,
    InMemoryUserGateway,
)


@pytest.fixture()
def make_handler():
    def _make_handler(user_id: UserId | None = None):
        identity_provider = InMemoryIdentityProvider(user_id=user_id)
        user_gateway = InMemoryUserGateway()
        shop_gateway = InMemoryShopGateway()

        handler = BotStartCommandHandler(
            identity_provider=identity_provider,
            user_gateway=user_gateway,
            shop_gateway=shop_gateway,
        )

        return handler, identity_provider, user_gateway, shop_gateway

    return _make_handler


@pytest.fixture()
def command() -> BotStartCommand:
    return BotStartCommand(tg_id=1, full_name="TestUser")


@pytest.mark.asyncio()
async def test_creates_new_user_when_not_exists(make_handler, command) -> None:
    handler, _, user_gateway, _ = make_handler()

    result = await handler.handle(command)

    assert result is False
    assert len(user_gateway.users) == 1


@pytest.mark.asyncio()
async def test_returns_false_when_user_has_no_shop(
    make_handler, command
) -> None:
    user_id = UserId(uuid.uuid4())
    handler, _, user_gateway, _ = make_handler(user_id=user_id)
    user_gateway.users[user_id] = {
        "tg_id": command.tg_id,
        "full_name": command.full_name,
    }

    result = await handler.handle(command)

    assert result is False


@pytest.mark.asyncio()
async def test_returns_true_when_user_has_shop(make_handler, command) -> None:
    user_id = UserId(uuid.uuid4())
    handler, _, user_gateway, shop_gateway = make_handler(user_id=user_id)
    user_gateway.users[user_id] = {
        "tg_id": command.tg_id,
        "full_name": command.full_name,
    }
    shop_gateway.linked_users.add(user_id)

    result = await handler.handle(command)

    assert result is True


@pytest.mark.asyncio()
async def test_full_flow_creates_and_links_user(make_handler, command) -> None:
    handler, idp, user_gateway, shop_gateway = make_handler()
    user_id = UserId(uuid.uuid4())

    # 1. User not exists
    result = await handler.handle(command)
    assert result is False
    assert len(user_gateway.users) == 1

    # 2. User exists, but not linked with shop
    idp.user_id = user_id
    result = await handler.handle(command)
    assert result is False

    # 3. User exists and linked with shop
    shop_gateway.linked_users.add(user_id)
    result = await handler.handle(command)
    assert result is True
