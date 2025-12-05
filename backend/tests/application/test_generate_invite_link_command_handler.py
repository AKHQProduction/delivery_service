import uuid

import pytest

from backend.application.errors import AccessDeniedError, FieldError
from backend.application.usecases.invite_employee import (
    GenerateInviteLinkCommand,
    GenerateInviteLinkCommandHandler,
)
from backend.application.usecases.invite_employee.interfaces import (
    GeneratedLink,
    InviteLinkGenerator,
)
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.in_memory import (
    InMemoryIdentityProvider,
    InMemoryLinkGateway,
)


class FakeInviteLinkGenerator(InviteLinkGenerator):
    def __init__(
        self,
        link: str = "https://t.me/bot?start=abc123",
        payload: str = "abc123",
    ):
        self.link = link
        self.payload = payload

    async def generate(self) -> GeneratedLink:
        return GeneratedLink(link=self.link, payload=self.payload)


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
        link_generator = FakeInviteLinkGenerator()
        link_gateway = InMemoryLinkGateway()

        handler = GenerateInviteLinkCommandHandler(
            idp=idp,
            link_generator=link_generator,
            link_gateway=link_gateway,
        )

        return handler, idp, link_generator, link_gateway

    return _make_handler


@pytest.mark.parametrize("role", (ShopRole.MANAGER, ShopRole.COURIER))
@pytest.mark.asyncio()
async def test_successfully_generate_invite_link_for_valid_roles(
    make_handler, role: ShopRole
) -> None:
    handler, _, link_generator, _ = make_handler(role=ShopRole.OWNER)
    command = GenerateInviteLinkCommand(role=role, full_name="John Doe")

    result = await handler.handle(command)

    assert result == link_generator.link


@pytest.mark.asyncio()
async def test_raise_access_denied_when_not_owner(make_handler) -> None:
    handler, _, _, _ = make_handler(role=ShopRole.MANAGER)
    command = GenerateInviteLinkCommand(
        role=ShopRole.COURIER, full_name="John Doe"
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_access_denied_when_courier_creates_link(
    make_handler,
) -> None:
    handler, _, _, _ = make_handler(role=ShopRole.COURIER)
    command = GenerateInviteLinkCommand(
        role=ShopRole.MANAGER, full_name="John Doe"
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_save_link_in_gateway(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, link_generator, link_gateway = make_handler(
        role=ShopRole.OWNER, shop_id=shop_id
    )
    command = GenerateInviteLinkCommand(
        role=ShopRole.MANAGER, full_name="John Doe"
    )

    await handler.handle(command)

    assert len(link_gateway.links) == 1
    saved_link_dict = next(iter(link_gateway.links.items()))
    saved_link = saved_link_dict[1]
    assert saved_link.payload == link_generator.payload
    assert saved_link.role == ShopRole.MANAGER
    assert saved_link.shop_id == shop_id
    assert saved_link.full_name == "John Doe"


@pytest.mark.asyncio()
async def test_raise_validation_error_when_role_is_owner() -> None:
    with pytest.raises(FieldError) as exc_info:
        GenerateInviteLinkCommand(role=ShopRole.OWNER, full_name="John Doe")

    assert exc_info.value._field == "role"
    assert exc_info.value._value == ShopRole.OWNER
    assert ShopRole.MANAGER in exc_info.value._acceptable_values
    assert ShopRole.COURIER in exc_info.value._acceptable_values
