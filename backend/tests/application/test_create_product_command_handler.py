import uuid

import pytest

from backend.application.commands.create_product import (
    CreateProductCommand,
    CreateProductCommandHandler,
)
from backend.application.errors import AccessDeniedError
from backend.application.vars import ProductCategory, ShopId, ShopRole, UserId
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryIdentityProvider,
)
from backend.infrastructure.in_memory.product_gateway import (
    InMemoryProductGateway,
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
        product_gateway = InMemoryProductGateway()
        tr_manager = FakeTransactionManager()

        handler = CreateProductCommandHandler(
            idp=idp, gateway=product_gateway, tr_manager=tr_manager
        )

        return handler, idp, product_gateway, tr_manager

    return _make_handler


@pytest.fixture()
def command() -> CreateProductCommand:
    return CreateProductCommand(
        name="Test Product", price=100, category=ProductCategory.WATER
    )


@pytest.mark.parametrize("role", (ShopRole.OWNER, ShopRole.MANAGER))
@pytest.mark.asyncio()
async def test_product_can_create_only_administration_role(
    make_handler, command: CreateProductCommand, role: ShopRole
) -> None:
    handler, _, _, _ = make_handler(role=role)

    result = await handler.handle(command)

    assert result


@pytest.mark.asyncio()
async def test_raise_error_when_not_admin_role_create_product(
    make_handler, command
) -> None:
    handler, _, _, _ = make_handler(role=ShopRole.COURIER)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_after_creating_save_in_db(make_handler, command) -> None:
    handler, _, gateway, tr_manager = make_handler(role=ShopRole.OWNER)

    await handler.handle(command)

    assert len(gateway.products) == 1
    assert tr_manager.committed
