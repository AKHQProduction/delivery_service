import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    GetProductsFilters,
)
from backend.application.vars import ProductCategory, ProductId, ShopId
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

    product = await product_gateway.read(product_id, shop_id)

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
    shop_id = ShopId(uuid.uuid4())

    product = await product_gateway.read(product_id, shop_id)

    assert product is None


@pytest.mark.asyncio()
async def test_read_all_products_with_name_filter(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id = await create_shop()

    # Create multiple products
    product_ids = []
    for i, name in enumerate(
        ["Water Bottle", "Water Gallon", "Soda Can"], start=1
    ):
        product_id = ProductId(uuid.uuid4())
        product_ids.append(product_id)
        product = Product(
            id=product_id,
            shop_id=shop_id,
            name=name,
            price=100 * i,
            category=ProductCategory.WATER.value,
        )
        session.add(product)
    await session.flush()

    # Test filter by name
    filters = GetProductsFilters(name="Water")
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 2
    assert all("Water" in p.name for p in products)
    assert products[0].name == "Water Bottle"
    assert products[1].name == "Water Gallon"


@pytest.mark.asyncio()
async def test_read_all_products_sorted_desc(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id = await create_shop()

    # Create products
    for name in ["Apple", "Banana", "Cherry"]:
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id,
            name=name,
            price=100,
            category=ProductCategory.OTHER.value,
        )
        session.add(product)
    await session.flush()

    filters = GetProductsFilters()
    pagination = Pagination(offset=0, limit=10, order=SortOrder.DESC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 3
    assert products[0].name == "Cherry"
    assert products[1].name == "Banana"
    assert products[2].name == "Apple"


@pytest.mark.asyncio()
async def test_read_all_products_with_pagination(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id = await create_shop()

    # Create 5 products
    for i in range(5):
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id,
            name=f"Product {i}",
            price=100,
            category=ProductCategory.WATER.value,
        )
        session.add(product)
    await session.flush()

    filters = GetProductsFilters()

    # Get first page
    pagination = Pagination(offset=0, limit=2, order=SortOrder.ASC)
    products_page1 = await product_gateway.read_all(filters, pagination)
    assert len(products_page1) == 2

    # Get second page
    pagination = Pagination(offset=2, limit=2, order=SortOrder.ASC)
    products_page2 = await product_gateway.read_all(filters, pagination)
    assert len(products_page2) == 2

    # Get third page
    pagination = Pagination(offset=4, limit=2, order=SortOrder.ASC)
    products_page3 = await product_gateway.read_all(filters, pagination)
    assert len(products_page3) == 1

    # Verify no duplicates
    all_ids = [
        p.product_id for p in products_page1 + products_page2 + products_page3
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.asyncio()
async def test_read_all_products_empty_result(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
) -> None:
    filters = GetProductsFilters(name="NonExistentProduct")
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 0


@pytest.mark.asyncio()
async def test_read_all_products_case_insensitive_filter(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id = await create_shop()

    product_id = ProductId(uuid.uuid4())
    product = Product(
        id=product_id,
        shop_id=shop_id,
        name="WaTeR BoTtLe",
        price=100,
        category=ProductCategory.WATER.value,
    )
    session.add(product)
    await session.flush()

    # Test case-insensitive search
    filters = GetProductsFilters(name="water")
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 1
    assert products[0].name == "WaTeR BoTtLe"


@pytest.mark.asyncio()
async def test_read_all_products_with_shop_id_filter(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id_1 = await create_shop()
    shop_id_2 = await create_shop()

    # Create products for shop 1
    for i in range(3):
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id_1,
            name=f"Shop1 Product {i}",
            price=100,
            category=ProductCategory.WATER.value,
        )
        session.add(product)

    # Create products for shop 2
    for i in range(2):
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id_2,
            name=f"Shop2 Product {i}",
            price=100,
            category=ProductCategory.OTHER.value,
        )
        session.add(product)
    await session.flush()

    # Filter by shop_id_1
    filters = GetProductsFilters(shop_id=shop_id_1)
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 3
    assert all("Shop1" in p.name for p in products)


@pytest.mark.asyncio()
async def test_read_all_products_with_shop_id_and_name_filter(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id_1 = await create_shop()
    shop_id_2 = await create_shop()

    # Create products for shop 1
    for name in ["Water Bottle", "Soda Can", "Water Gallon"]:
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id_1,
            name=name,
            price=100,
            category=ProductCategory.WATER.value,
        )
        session.add(product)

    # Create products for shop 2
    for name in ["Water Bottle", "Juice"]:
        product_id = ProductId(uuid.uuid4())
        product = Product(
            id=product_id,
            shop_id=shop_id_2,
            name=name,
            price=100,
            category=ProductCategory.OTHER.value,
        )
        session.add(product)
    await session.flush()

    # Filter by shop_id_1 and name containing "Water"
    filters = GetProductsFilters(shop_id=shop_id_1, name="Water")
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 2
    assert all("Water" in p.name for p in products)
    assert products[0].name == "Water Bottle"
    assert products[1].name == "Water Gallon"


@pytest.mark.asyncio()
async def test_read_all_products_no_filters(
    product_gateway: SQLAlchemyProductGateway,
    session: AsyncSession,
    create_shop,
) -> None:
    shop_id_1 = await create_shop()
    shop_id_2 = await create_shop()

    # Create products for different shops
    for shop_id in [shop_id_1, shop_id_2]:
        for i in range(2):
            product_id = ProductId(uuid.uuid4())
            product = Product(
                id=product_id,
                shop_id=shop_id,
                name=f"Product {i}",
                price=100,
                category=ProductCategory.WATER.value,
            )
            session.add(product)
    await session.flush()

    # No filters - should return all products
    filters = GetProductsFilters()
    pagination = Pagination(offset=0, limit=10, order=SortOrder.ASC)

    products = await product_gateway.read_all(filters, pagination)

    assert len(products) == 4
