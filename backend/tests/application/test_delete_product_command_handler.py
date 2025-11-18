import uuid

import pytest

from backend.application.commands.delete_product import (
    DeleteProductCommand,
    DeleteProductCommandHandler,
)
from backend.application.errors import AccessDeniedError
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
)
from backend.application.vars import (
    ProductCategory,
    ProductId,
    ShopId,
    ShopRole,
    UserId,
)
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

        handler = DeleteProductCommandHandler(
            idp=idp, product_gateway=product_gateway, tr_manager=tr_manager
        )

        return handler, idp, product_gateway, tr_manager

    return _make_handler


@pytest.mark.asyncio()
async def test_delete_product_success(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name="Test Product",
            price=100,
            category=ProductCategory.WATER,
        )
    )

    command = DeleteProductCommand(product_id=product_id)

    await handler.handle(command)

    deleted_product = await product_gateway.load(product_id)
    assert deleted_product is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_access_denied_no_management_rights(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    product_id = ProductId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name="Test Product",
            price=100,
            category=ProductCategory.WATER,
        )
    )

    command = DeleteProductCommand(product_id=product_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    product = await product_gateway.load(product_id)
    assert product is not None
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_product_id = ProductId(uuid.uuid4())

    command = DeleteProductCommand(product_id=non_existent_product_id)

    await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_product_access_denied_different_shop(
    make_handler,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())

    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=other_shop_id,
            name="Test Product",
            price=100,
            category=ProductCategory.WATER,
        )
    )

    command = DeleteProductCommand(product_id=product_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    product = await product_gateway.load(product_id)
    assert product is not None
    assert not tr_manager.committed
