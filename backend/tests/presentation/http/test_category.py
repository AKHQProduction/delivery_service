import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import CategoryId, ShopRole
from backend.infrastructure.persistence.tables import Category

BASE_URL = "/api/v1/categories"


@pytest.mark.asyncio()
async def test_create_category(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)
    name = "Water"

    json = {"name": name}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    await session.flush()

    new_entity = await session.execute(
        select(Category).where(Category.name == name)
    )
    rows = new_entity.fetchall()
    assert len(rows) == 1

    category = rows[0][0]
    assert category.name == name


@pytest.mark.asyncio()
async def test_create_category_duplicate_name_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await setup_test_category(shop_id=shop_id, name="Water")
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Water"}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_edit_category(
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
    new_name = "Beverages"

    json = {"name": new_name}
    url = BASE_URL + f"/{category_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    updated_entity = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    rows = updated_entity.fetchall()
    assert len(rows) == 1

    category = rows[0][0]
    assert category.name == new_name


@pytest.mark.asyncio()
async def test_edit_category_duplicate_name_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await setup_test_category(shop_id=shop_id, name="Water")
    category_id = await setup_test_category(shop_id=shop_id, name="Other")
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Water"}
    url = BASE_URL + f"/{category_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_delete_category(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    category_id = await setup_test_category(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{category_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()

    deleted_entity = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    assert deleted_entity.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_get_all_categories(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    categories_data = ["Water", "Beverages", "Accessories"]

    for name in categories_data:
        await session.execute(
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
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
    assert result[0]["name"] == "Accessories"
    assert result[1]["name"] == "Beverages"
    assert result[2]["name"] == "Water"


@pytest.mark.asyncio()
async def test_get_all_categories_with_name_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    categories_data = ["Water Bottles", "Water Gallons", "Accessories"]

    for name in categories_data:
        await session.execute(
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
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
    assert all("Water" in c["name"] for c in result)


@pytest.mark.asyncio()
async def test_get_all_categories_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for i in range(5):
        await session.execute(
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id,
                name=f"Category {i}",
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
        c["category_id"] for c in result_page1 + result_page2 + result_page3
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.asyncio()
async def test_get_all_categories_sorted_desc(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for name in ["Apple", "Banana", "Cherry"]:
        await session.execute(
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
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
async def test_get_all_categories_filters_by_shop_id(
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
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id_1,
                name=f"Shop1 Category {i}",
            )
        )

    # Create categories for shop 2 (should not be returned)
    for i in range(2):
        await session.execute(
            insert(Category).values(
                id=CategoryId(uuid.uuid4()),
                shop_id=shop_id_2,
                name=f"Shop2 Category {i}",
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(url=url, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    # Should only return categories from shop 1
    assert len(result) == 3
    assert all("Shop1" in c["name"] for c in result)


@pytest.mark.asyncio()
async def test_create_category_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "Water"}
    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_create_category_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1100
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Water"}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_category_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_edit_category_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1101
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    category_id = await setup_test_category(shop_id=shop_id, name="Water")
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{category_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_category_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1102
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_category_unauthorized(
    http_client: AsyncClient,
) -> None:
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_delete_category_as_courier_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_category,
) -> None:
    telegram_id = 1103
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.COURIER
    )
    category_id = await setup_test_category(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{category_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_category_not_found_returns_ok(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 1104
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
