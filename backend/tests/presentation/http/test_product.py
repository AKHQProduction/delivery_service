from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ProductCategory
from backend.infrastructure.persistence.tables import Product

BASE_URL = "/api/v1/products"


@pytest.mark.asyncio()
async def test_new_product_endpoint(
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
    category = ProductCategory.WATER

    json = {"name": name, "price": price, "category": category}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    await session.flush()

    new_entity = await session.execute(
        select(Product).where(
            Product.name == name,
            Product.category == category,
            Product.price == price,
        )
    )
    rows = new_entity.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == name
    assert product.price == price
    assert product.category == category


@pytest.mark.asyncio()
async def test_edit_all_product_fields(
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
    new_price = 150
    new_category = ProductCategory.OTHER

    json = {"name": new_name, "price": new_price, "category": new_category}
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
    assert product.category == new_category


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

    assert response.status_code == status.HTTP_200_OK
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
    product_id, name, price, category = await setup_test_product(
        shop_id=shop_id
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{product_id}"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    assert response.json()["product_id"] == str(product_id)
    assert response.json()["name"] == name
    assert response.json()["price"] == price
    assert response.json()["category"] == category
