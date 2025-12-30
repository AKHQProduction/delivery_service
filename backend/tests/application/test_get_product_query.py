import uuid

import pytest

from backend.application.errors import EntityNotFoundError
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
)
from backend.application.queries.get_product import GetProductQueryHandler
from backend.application.vars import (
    ProductId,
    ShopId,
    ShopRole,
    UserId,
)
from backend.infrastructure.in_memory import InMemoryIdentityProvider
from backend.infrastructure.in_memory.product_gateway import (
    InMemoryProductGateway,
)


@pytest.fixture()
def make_query():
    def _make_query(
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

        query = GetProductQueryHandler(
            idp=idp, product_gateway=product_gateway
        )

        return query, idp, product_gateway

    return _make_query


@pytest.mark.asyncio()
async def test_get_product_success(make_query) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    query, _, product_gateway = make_query(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    product_id = ProductId(uuid.uuid4())
    product_name = "Test Product"
    product_price = 100

    await product_gateway.create_product(
        CreateProductDTO(
            product_id=product_id,
            shop_id=shop_id,
            name=product_name,
            price=product_price,
            category_id=None,
        )
    )

    result = await query.handle(product_id)

    assert result is not None
    assert result.product_id == product_id
    assert result.name == product_name
    assert result.price == product_price
    assert result.category_id is None


@pytest.mark.asyncio()
async def test_get_product_not_found(make_query) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    query, _, _ = make_query(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_product_id = ProductId(uuid.uuid4())

    with pytest.raises(EntityNotFoundError) as exc_info:
        await query.handle(non_existent_product_id)

    assert exc_info.value.message == "Product not found"


@pytest.mark.asyncio()
async def test_get_product_accessible_by_different_roles(make_query) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    _, _, product_gateway = make_query(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
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

    for role in [ShopRole.OWNER, ShopRole.MANAGER, ShopRole.COURIER]:
        query, _, _ = make_query(
            user_id=UserId(uuid.uuid4()), shop_id=shop_id, role=role
        )
        query._product_gateway = product_gateway

        result = await query.handle(product_id)

        assert result is not None
        assert result.product_id == product_id
        assert result.name == "Test Product"
