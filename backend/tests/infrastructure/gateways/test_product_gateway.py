import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
)
from backend.application.vars import ProductCategory, ProductId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
)
from backend.infrastructure.persistence.tables import Product


@pytest.mark.asyncio()
async def test_create_product(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id = await create_shop()
    product_id = ProductId(uuid.uuid4())
    await session.flush()

    product_dto = CreateProductDTO(
        product_id=product_id,
        shop_id=shop_id,
        name="Test Water",
        price=100,
        category=ProductCategory.WATER,
    )

    await product_gateway.create_product(product_dto)
    await session.flush()

    result = await session.execute(
        select(Product).where(Product.id == product_dto.product_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    product = rows[0][0]
    assert product.name == product_dto.name
    assert product.price == product_dto.price
    assert product.category == product_dto.category.value
    assert product.shop_id == shop_id


def test_return_product_id(product_gateway: SQLAlchemyProductGateway) -> None:
    result = product_gateway.next_id()

    assert isinstance(result, uuid.UUID)
    assert result.version == 7


def test_return_unique_product_ids(
    product_gateway: SQLAlchemyProductGateway,
) -> None:
    id1 = product_gateway.next_id()
    id2 = product_gateway.next_id()
    id3 = product_gateway.next_id()

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3
    assert all(
        isinstance(product_id, uuid.UUID) for product_id in [id1, id2, id3]
    )


@pytest.mark.asyncio()
async def test_load_product(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    setup_test_product,
    create_shop,
) -> None:
    shop_id = await create_shop()
    product_id, _, _, _ = await setup_test_product(shop_id)
    await session.flush()

    product = await product_gateway.load(product_id)

    assert product is not None
    assert product.product_id == product_id
    assert product.shop_id == shop_id
    assert product.name == "Test Product"
    assert product.price == 100
    assert product.category == ProductCategory.WATER


@pytest.mark.asyncio()
async def test_load_product_returns_none_when_not_exists(
    product_gateway: SQLAlchemyProductGateway,
) -> None:
    product_id = ProductId(uuid.uuid4())

    product = await product_gateway.load(product_id)

    assert product is None


@pytest.mark.asyncio()
async def test_update_product(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    setup_test_product,
    create_shop,
) -> None:
    shop_id = await create_shop()
    product_id, _, _, _ = await setup_test_product(shop_id)
    await session.flush()

    product = await product_gateway.load(product_id)
    assert product is not None

    product.name = "Updated Product"
    product.price = 200
    product.category = ProductCategory.OTHER

    await product_gateway.update(product)
    await session.flush()

    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    updated_product_db = result.scalar_one()

    assert updated_product_db.name == "Updated Product"
    assert updated_product_db.price == 200
    assert updated_product_db.category == ProductCategory.OTHER.value


@pytest.mark.asyncio()
async def test_delete_product(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    setup_test_product,
    create_shop,
) -> None:
    shop_id = await create_shop()
    product_id, _, _, _ = await setup_test_product(shop_id)
    await session.flush()

    product_before = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    assert product_before.scalar_one() is not None

    await product_gateway.delete(product_id)
    await session.flush()

    product_after = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    assert product_after.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_delete_product_not_exists(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
) -> None:
    non_existent_product_id = ProductId(uuid.uuid4())

    await product_gateway.delete(non_existent_product_id)
    await session.flush()


@pytest.mark.asyncio()
async def test_read_product(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    setup_test_product,
    create_shop,
) -> None:
    shop_id = await create_shop()
    product_id, _, _, _ = await setup_test_product(shop_id)
    await session.flush()

    product = await product_gateway.read(product_id)

    assert product is not None
    assert product.product_id == product_id
    assert product.name == "Test Product"
    assert product.price == 100
    assert product.category == ProductCategory.WATER


@pytest.mark.asyncio()
async def test_read_product_returns_none_when_not_exists(
    product_gateway: SQLAlchemyProductGateway,
) -> None:
    product_id = ProductId(uuid.uuid4())

    product = await product_gateway.read(product_id)

    assert product is None
