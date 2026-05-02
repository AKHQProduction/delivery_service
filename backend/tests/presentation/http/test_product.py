import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ProductId, ShopRole
from backend.infrastructure.persistence.tables import Product

BASE_URL = "/api/v1/products"


@pytest.mark.asyncio()
async def test_new_product_endpoint_without_category(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    name = "Test Product"
    price = 100

    json = {"name": name, "price": price}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    await session.flush()

    new_entity = await session.execute(
        select(Product).where(
            Product.name == name,
            Product.price == price,
        )
    )
    rows = new_entity.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == name
    assert product.price == price
    assert product.category_id is None


@pytest.mark.asyncio()
async def test_new_product_endpoint_with_category(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    category_id = await setup_test_category(shop_id=shop_id, name="Water")
    await session.commit()

    headers = customer_headers(telegram_id)

    name = "Test Product"
    price = 100

    json = {"name": name, "price": price, "category_id": str(category_id)}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    await session.flush()

    new_entity = await session.execute(
        select(Product).where(
            Product.name == name,
            Product.price == price,
        )
    )
    rows = new_entity.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == name
    assert product.price == price
    assert product.category_id == category_id


@pytest.mark.asyncio()
async def test_edit_all_product_fields(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    new_category_id = await setup_test_category(shop_id=shop_id, name="Other")
    await session.commit()

    headers = customer_headers(telegram_id)
    new_name = "NewName"
    new_price = 150

    json = {
        "name": new_name,
        "price": new_price,
        "category_id": str(new_category_id),
    }
    url = BASE_URL + f"/{product_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    updated_entity = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    rows = updated_entity.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == new_name
    assert product.price == new_price
    assert product.category_id == new_category_id


@pytest.mark.asyncio()
async def test_edit_product_remove_category_with_empty(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    category_id = await setup_test_category(shop_id=shop_id, name="Water")
    product_id, _, _, _ = await setup_test_product(
        shop_id=shop_id, category_id=category_id
    )
    await session.commit()

    # Verify product has category
    entity = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product = entity.scalar_one()
    assert product.category_id == category_id

    headers = customer_headers(telegram_id)

    json = {"category_id": "EMPTY"}
    url = BASE_URL + f"/{product_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_200_OK

    # Flush and re-fetch from DB to get updated value
    await session.flush()
    updated_entity = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    updated_product = updated_entity.scalar_one()
    assert updated_product.category_id is None


@pytest.mark.asyncio()
async def test_edit_one_product_fields(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)
    new_name = "NewName"

    json = {"name": new_name}
    url = BASE_URL + f"/{product_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    updated_entity = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    rows = updated_entity.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == new_name


@pytest.mark.asyncio()
async def test_delete_product(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{product_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()

    deleted_entity = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    assert deleted_entity.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_get_product(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    product_id, name, price, _ = await setup_test_product(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{product_id}"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    assert response.json()["product_id"] == str(product_id)
    assert response.json()["name"] == name
    assert response.json()["price"] == price
    assert response.json()["category_id"] is None


@pytest.mark.asyncio()
async def test_get_all_products(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    products_data = [
        ("Water Bottle", 100),
        ("Water Gallon", 200),
        ("Soda Can", 50),
    ]

    for name, price in products_data:
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
                price=price,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    assert len(result) == 3
    assert result[0]["name"] == "Soda Can"
    assert result[1]["name"] == "Water Bottle"
    assert result[2]["name"] == "Water Gallon"


@pytest.mark.asyncio()
async def test_get_all_products_with_name_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    products_data = [
        ("Water Bottle", 100),
        ("Water Gallon", 200),
        ("Soda Can", 50),
    ]

    for name, price in products_data:
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
                price=price,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(
        url=url, headers=headers, params={"name": "Water"}
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    assert len(result) == 2
    assert all("Water" in p["name"] for p in result)
    assert result[0]["name"] == "Water Bottle"
    assert result[1]["name"] == "Water Gallon"


@pytest.mark.asyncio()
async def test_get_all_products_with_category_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    water_category_id = await setup_test_category(
        shop_id=shop_id, name="Water"
    )
    soda_category_id = await setup_test_category(shop_id=shop_id, name="Soda")

    for name, category_id in [
        ("Water Bottle", water_category_id),
        ("Soda Can", soda_category_id),
        ("No Category", None),
    ]:
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
                price=100,
                category_id=category_id,
            )
        )
    await session.commit()

    response = await http_client.get(
        url=BASE_URL + "/all",
        headers=customer_headers(telegram_id),
        params={"category_id": str(water_category_id)},
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 1
    assert result[0]["name"] == "Water Bottle"
    assert result[0]["category_id"] == str(water_category_id)


@pytest.mark.asyncio()
async def test_get_product_summary_counts_all_matching_products(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    water_category_id = await setup_test_category(
        shop_id=shop_id, name="Water"
    )
    soda_category_id = await setup_test_category(shop_id=shop_id, name="Soda")

    for name, category_id in [
        ("Water Bottle", water_category_id),
        ("Water Gallon", water_category_id),
        ("Soda Can", soda_category_id),
        ("Water Without Category", None),
    ]:
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
                price=100,
                category_id=category_id,
            )
        )
    await session.commit()

    response = await http_client.get(
        url=BASE_URL + "/summary",
        headers=customer_headers(telegram_id),
        params={"name": "Water"},
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    counts = {
        item["category_id"]: item["count"]
        for item in result["category_counts"]
    }

    assert result["total_count"] == 3
    assert counts[str(water_category_id)] == 2
    assert counts[None] == 1
    assert str(soda_category_id) not in counts


@pytest.mark.asyncio()
async def test_get_all_products_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for i in range(5):
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=f"Product {i}",
                price=100,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"

    # Get first page
    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page1 = response.json()
    assert len(result_page1) == 2

    # Get second page
    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page2 = response.json()
    assert len(result_page2) == 2

    # Get third page
    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 4}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page3 = response.json()
    assert len(result_page3) == 1

    # Verify no duplicates
    all_ids = [
        p["product_id"] for p in result_page1 + result_page2 + result_page3
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.asyncio()
async def test_get_all_products_sorted_desc(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for name in ["Apple", "Banana", "Cherry"]:
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
                price=100,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(
        url=url, headers=headers, params={"order": "DESC"}
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    assert len(result) == 3
    assert result[0]["name"] == "Cherry"
    assert result[1]["name"] == "Banana"
    assert result[2]["name"] == "Apple"


@pytest.mark.asyncio()
async def test_get_all_products_filters_by_shop_id(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_shop,
) -> None:
    telegram_id = 1000
    _, shop_id_1 = await setup_full_test_user_with_shop(
        telegram_id=telegram_id
    )
    shop_id_2 = await create_shop()

    for i in range(3):
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id_1,
                name=f"Shop1 Product {i}",
                price=100,
            )
        )

    # Create products for shop 2 (should not be returned)
    for i in range(2):
        await session.execute(
            insert(Product).values(
                id=ProductId(uuid.uuid4()),
                shop_id=shop_id_2,
                name=f"Shop2 Product {i}",
                price=100,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    # Should only return products from shop 1
    assert len(result) == 3
    assert all("Shop1" in p["name"] for p in result)


@pytest.mark.asyncio()
async def test_create_product_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "Test Product", "price": 100}
    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_create_product_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1200
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Test Product", "price": 100}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_product_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_edit_product_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
) -> None:
    telegram_id = 1201
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{product_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_product_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1202
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_product_unauthorized(
    http_client: AsyncClient,
) -> None:
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_delete_product_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_product,
) -> None:
    telegram_id = 1203
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{product_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_product_not_found_returns_ok(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1204
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_get_product_unauthorized(
    http_client: AsyncClient,
) -> None:
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.get(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_get_product_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1205
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
