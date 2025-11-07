import pytest

from backend.application.commands import (
    BotStartCommand,
    BotStartCommandHandler,
)
from backend.infrastructure.in_memory import (
    InMemoryIdentityProvider,
    InMemoryShopGateway,
    InMemoryUserGateway,
)


@pytest.mark.asyncio()
async def test_full_flow_creates_and_links_user() -> None:
    command = BotStartCommand(tg_id=1, full_name="TestUser")
    identity = InMemoryIdentityProvider(user_id=None)
    user_gateway = InMemoryUserGateway()
    shop_gateway = InMemoryShopGateway()

    handler = BotStartCommandHandler(identity, user_gateway, shop_gateway)
    result = await handler.handle(command)

    assert result is False
    assert len(user_gateway.users) == 1

    user_id = next(iter(user_gateway.users))
    identity.user_id = user_id
    result = await handler.handle(command)
    assert result is False

    shop_gateway.linked_users.add(user_id)
    result = await handler.handle(command)
    assert result is True
