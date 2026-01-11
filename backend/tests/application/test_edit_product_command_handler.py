import uuid

import pytest

from backend.application.commands.edit_product import (
    EditProductCommand,
    EditProductCommandHandler,
)
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
)
from backend.application.vars import (
    CategoryId,
    Empty,
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

        handler = EditProductCommandHandler(
            idp=idp, product_gateway=product_gateway, tr_manager=tr_manager
        )

        return handler, idp, product_gateway, tr_manager

    return _make_handler


@pytest.mark.asyncio()
async def test_edit_product_all_fields(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    new_category_id = CategoryId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name="Old Product",
            price=100,
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_name="New Product",
        new_price=200,
        new_category_id=new_category_id,
    )

    await handler.handle(command)

    updated_product = await product_gateway.load(product_id)
    assert updated_product is not None
    assert updated_product.name == "New Product"
    assert updated_product.price == 200
    assert updated_product.category_id == new_category_id
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_only_name(make_handler) -> None:
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
            name="Old Product",
            price=100,
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_name="New Product",
    )

    await handler.handle(command)

    updated_product = await product_gateway.load(product_id)
    assert updated_product is not None
    assert updated_product.name == "New Product"
    assert updated_product.price == 100
    assert updated_product.category_id is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_only_price(make_handler) -> None:
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
            name="Old Product",
            price=100,
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_price=200,
    )

    await handler.handle(command)

    updated_product = await product_gateway.load(product_id)
    assert updated_product is not None
    assert updated_product.name == "Old Product"
    assert updated_product.price == 200
    assert updated_product.category_id is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_only_category(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    new_category_id = CategoryId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name="Old Product",
            price=100,
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_category_id=new_category_id,
    )

    await handler.handle(command)

    updated_product = await product_gateway.load(product_id)
    assert updated_product is not None
    assert updated_product.name == "Old Product"
    assert updated_product.price == 100
    assert updated_product.category_id == new_category_id
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_remove_category_with_empty(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, product_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    initial_category_id = CategoryId(uuid.uuid4())
    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name="Product with Category",
            price=100,
            category_id=initial_category_id,
        )
    )

    # Verify product has category
    product_before = await product_gateway.load(product_id)
    assert product_before is not None
    assert product_before.category_id == initial_category_id

    # Remove category using Empty.EMPTY
    command = EditProductCommand(
        product_id=product_id,
        new_category_id=Empty.EMPTY,
    )

    await handler.handle(command)

    updated_product = await product_gateway.load(product_id)
    assert updated_product is not None
    assert updated_product.name == "Product with Category"
    assert updated_product.price == 100
    assert updated_product.category_id is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_access_denied_no_management_rights(
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
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_name="Updated Product",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_product_id = ProductId(uuid.uuid4())

    command = EditProductCommand(
        product_id=non_existent_product_id,
        new_name="Updated Product",
    )

    with pytest.raises(EntityNotFoundError):
        await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_edit_product_access_denied_different_shop(make_handler) -> None:
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
            category_id=None,
        )
    )

    command = EditProductCommand(
        product_id=product_id,
        new_name="Updated Product",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    assert not tr_manager.committed
