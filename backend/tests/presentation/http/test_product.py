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

    result = await session.execute(
        select(Product).where(
            Product.name == name,
            Product.category == category,
            Product.price == price,
        )
    )
    rows = result.fetchall()
    assert len(rows) == 1

    product = rows[0][0]
    assert product.name == name
    assert product.price == price
    assert product.category == category
