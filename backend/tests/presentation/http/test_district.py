import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import DistrictId, ShopRole
from backend.infrastructure.persistence.tables.districts import District

BASE_URL = "/api/v1/districts"


@pytest.mark.asyncio()
async def test_create_district(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2000
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)
    name = "Центральный"

    json = {"name": name}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_201_CREATED
    await session.flush()

    new_entity = await session.execute(
        select(District).where(District.name == name)
    )
    rows = new_entity.fetchall()
    assert len(rows) == 1

    district = rows[0][0]
    assert district.name == name


@pytest.mark.asyncio()
async def test_create_district_duplicate_name_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2001
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await setup_test_district(shop_id=shop_id, name="Центральный")
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Центральный"}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_edit_district(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2002
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    district_id = await setup_test_district(
        shop_id=shop_id, name="Центральный"
    )
    await session.commit()

    headers = customer_headers(telegram_id)
    new_name = "Северный"

    json = {"name": new_name}
    url = BASE_URL + f"/{district_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_200_OK
    await session.flush()

    updated_entity = await session.execute(
        select(District).where(District.id == district_id)
    )
    rows = updated_entity.fetchall()
    assert len(rows) == 1

    district = rows[0][0]
    assert district.name == new_name


@pytest.mark.asyncio()
async def test_edit_district_duplicate_name_conflict(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2003
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await setup_test_district(shop_id=shop_id, name="Центральный")
    district_id = await setup_test_district(shop_id=shop_id, name="Северный")
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Центральный"}
    url = BASE_URL + f"/{district_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio()
async def test_delete_district(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2004
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    district_id = await setup_test_district(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{district_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()

    deleted_entity = await session.execute(
        select(District).where(District.id == district_id)
    )
    assert deleted_entity.scalar_one_or_none() is None


@pytest.mark.asyncio()
async def test_get_all_districts(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2005
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    districts_data = ["Центральный", "Северный", "Южный"]

    for name in districts_data:
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
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
    assert result[0]["name"] == "Северный"
    assert result[1]["name"] == "Центральный"
    assert result[2]["name"] == "Южный"


@pytest.mark.asyncio()
async def test_get_all_districts_with_name_filter(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2006
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    districts_data = ["Центральный", "Центральный-2", "Северный"]

    for name in districts_data:
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
                shop_id=shop_id,
                name=name,
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"
    response = await http_client.get(
        url=url, headers=headers, params={"name": "Центральный"}
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()

    assert len(result) == 2
    assert all("Центральный" in d["name"] for d in result)


@pytest.mark.asyncio()
async def test_get_all_districts_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2007
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for i in range(5):
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
                shop_id=shop_id,
                name=f"District {i}",
            )
        )
    await session.flush()
    await session.commit()

    headers = customer_headers(telegram_id)
    url = BASE_URL + "/all"

    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 0}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page1 = response.json()
    assert len(result_page1) == 2

    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 2}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page2 = response.json()
    assert len(result_page2) == 2

    response = await http_client.get(
        url=url, headers=headers, params={"limit": 2, "offset": 4}
    )
    assert response.status_code == status.HTTP_200_OK
    result_page3 = response.json()
    assert len(result_page3) == 1

    all_ids = [
        d["district_id"] for d in result_page1 + result_page2 + result_page3
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.asyncio()
async def test_get_all_districts_sorted_desc(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2008
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)

    for name in ["Alpha", "Beta", "Gamma"]:
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
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
    assert result[0]["name"] == "Gamma"
    assert result[1]["name"] == "Beta"
    assert result[2]["name"] == "Alpha"


@pytest.mark.asyncio()
async def test_get_all_districts_filters_by_shop_id(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_shop,
) -> None:
    telegram_id = 2009
    _, shop_id_1 = await setup_full_test_user_with_shop(
        telegram_id=telegram_id
    )
    shop_id_2 = await create_shop()

    for i in range(3):
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
                shop_id=shop_id_1,
                name=f"Shop1 District {i}",
            )
        )

    for i in range(2):
        await session.execute(
            insert(District).values(
                id=DistrictId(uuid.uuid4()),
                shop_id=shop_id_2,
                name=f"Shop2 District {i}",
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
    assert all("Shop1" in d["name"] for d in result)


@pytest.mark.asyncio()
async def test_create_district_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "Центральный"}
    response = await http_client.post(url=BASE_URL, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_create_district_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2100
    await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Центральный"}
    response = await http_client.post(url=BASE_URL, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_district_unauthorized(
    http_client: AsyncClient,
) -> None:
    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, json=json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_edit_district_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2101
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    district_id = await setup_test_district(
        shop_id=shop_id, name="Центральный"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{district_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_edit_district_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2102
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "NewName"}
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_district_unauthorized(
    http_client: AsyncClient,
) -> None:
    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_delete_district_as_manager_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
) -> None:
    telegram_id = 2103
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=ShopRole.MANAGER
    )
    district_id = await setup_test_district(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{district_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_district_not_found_returns_ok(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    telegram_id = 2104
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{uuid.uuid4()}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_edit_district_cross_shop_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
    create_shop,
) -> None:
    telegram_id = 2200
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    other_shop_id = await create_shop()
    district_id = await setup_test_district(
        shop_id=other_shop_id, name="Чужой район"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    json = {"name": "Новое имя"}
    url = BASE_URL + f"/{district_id}"
    response = await http_client.patch(url=url, headers=headers, json=json)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_district_cross_shop_forbidden(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_district,
    create_shop,
) -> None:
    telegram_id = 2201
    await setup_full_test_user_with_shop(telegram_id=telegram_id)
    other_shop_id = await create_shop()
    district_id = await setup_test_district(
        shop_id=other_shop_id, name="Чужой район"
    )
    await session.commit()

    headers = customer_headers(telegram_id)

    url = BASE_URL + f"/{district_id}"
    response = await http_client.delete(url=url, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
