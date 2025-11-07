from uuid import UUID

import pytest

from backend.application.commands import (
    BotStartCommand,
    BotStartCommandHandler,
)
from backend.application.interfaces import (
    CreateUserViaTgDTO,
    ShopGateway,
    UserGateway,
)
from backend.application.interfaces.idp import IdentityProvider
from backend.application.vars import UserId


@pytest.mark.asyncio()
async def test_new_user_creates_and_returns_false() -> None:
    class FakeIdentityProvider(IdentityProvider):
        async def current_user_id(self) -> UserId | None:
            return None

    class FakeUserGateway(UserGateway):
        def __init__(self) -> None:
            self.created = False

        async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
            self.created = True

        def next_id(self) -> UserId:
            return UserId(UUID("019a6012-4d3f-7beb-8639-1119768d6590"))

    class FakeShopGateway(ShopGateway):
        async def relate_to_shop(self, user_id: UserId) -> bool:
            return False

    command = BotStartCommand(tg_id=1, full_name="TestUser")
    handler = BotStartCommandHandler(
        identity_provider=FakeIdentityProvider(),
        user_gateway=FakeUserGateway(),
        shop_gateway=FakeShopGateway(),
    )

    result = await handler.handle(command=command)

    assert isinstance(result, bool)
    assert result is False


@pytest.mark.asyncio()
async def test_existing_user_without_shop_returns_false() -> None:
    class FakeIdentityProvider(IdentityProvider):
        async def current_user_id(self) -> UserId | None:
            return UserId(UUID("019a6012-4d3f-7beb-8639-1119768d6590"))

    class FakeUserGateway(UserGateway):
        async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
            msg = "Should not create"
            raise AssertionError(msg)

        def next_id(self) -> UserId:
            msg = "Should not call"
            raise AssertionError(msg)

    class FakeShopGateway(ShopGateway):
        async def relate_to_shop(self, user_id: UserId) -> bool:
            return False

    command = BotStartCommand(tg_id=1, full_name="TestUser")
    handler = BotStartCommandHandler(
        identity_provider=FakeIdentityProvider(),
        user_gateway=FakeUserGateway(),
        shop_gateway=FakeShopGateway(),
    )

    result = await handler.handle(command=command)

    assert isinstance(result, bool)
    assert result is False


@pytest.mark.asyncio()
async def test_existing_user_with_shop_returns_true() -> None:
    class FakeIdentityProvider(IdentityProvider):
        async def current_user_id(self) -> UserId | None:
            return UserId(UUID("019a6012-4d3f-7beb-8639-1119768d6590"))

    class FakeUserGateway(UserGateway):
        async def create_user_via_tg(self, data: CreateUserViaTgDTO) -> None:
            msg = "Should not create"
            raise AssertionError(msg)

        def next_id(self) -> UserId:
            msg = "Should not call"
            raise AssertionError(msg)

    class FakeShopGateway(ShopGateway):
        async def relate_to_shop(self, user_id: UserId) -> bool:
            return True

    command = BotStartCommand(tg_id=1, full_name="TestUser")
    handler = BotStartCommandHandler(
        identity_provider=FakeIdentityProvider(),
        user_gateway=FakeUserGateway(),
        shop_gateway=FakeShopGateway(),
    )

    result = await handler.handle(command=command)

    assert isinstance(result, bool)
    assert result is True
