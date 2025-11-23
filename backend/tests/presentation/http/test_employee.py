import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopRole, UserId
from backend.infrastructure.persistence.tables import ShopMembership

BASE_URL = "/api/v1/employee"


@pytest.mark.asyncio()
async def test_update_employee_role_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 1000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=10, name=ShopRole.COURIER)
    manager_role_id = await create_role(role_id=11, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    json_data = {"role": ShopRole.MANAGER.value}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the update in database
    await session.flush()
    result = await session.execute(
        select(ShopMembership).where(
            ShopMembership.user_id == employee_user_id
        )
    )
    membership = result.scalar_one()
    assert membership.role_id == manager_role_id


@pytest.mark.asyncio()
async def test_update_employee_name_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 2000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=20, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    new_name = "Jane Smith"
    json_data = {"name": new_name}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the update in database
    await session.flush()
    result = await session.execute(
        select(ShopMembership).where(
            ShopMembership.user_id == employee_user_id
        )
    )
    membership = result.scalar_one()
    assert membership.name == new_name


@pytest.mark.asyncio()
async def test_update_employee_both_role_and_name(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 3000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=30, name=ShopRole.COURIER)
    manager_role_id = await create_role(role_id=31, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    new_name = "Jane Smith"
    json_data = {"role": ShopRole.MANAGER.value, "name": new_name}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the update in database
    await session.flush()
    result = await session.execute(
        select(ShopMembership).where(
            ShopMembership.user_id == employee_user_id
        )
    )
    membership = result.scalar_one()
    assert membership.role_id == manager_role_id
    assert membership.name == new_name


@pytest.mark.asyncio()
async def test_update_employee_denied_for_manager(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    manager_telegram_id = 4000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=manager_telegram_id, role=ShopRole.MANAGER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=40, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(manager_telegram_id)
    json_data = {"role": ShopRole.MANAGER.value}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_employee_denied_for_courier(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    courier_telegram_id = 5000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=courier_telegram_id, role=ShopRole.COURIER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=50, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(courier_telegram_id)
    json_data = {"name": "Jane Smith"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_employee_validation_error_for_owner_role(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 6000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=60, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    json_data = {"role": ShopRole.OWNER.value}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio()
async def test_update_employee_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    owner_telegram_id = 7000
    await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    non_existent_user_id = UserId(uuid.uuid4())
    json_data = {"role": ShopRole.MANAGER.value}

    response = await http_client.patch(
        url=f"{BASE_URL}/{non_existent_user_id}",
        headers=headers,
        json=json_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_employee_from_different_shop_denied(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 8000
    _, _ = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create employee in a different shop
    shop_id_2 = await create_shop(name="Another Shop")
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=80, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id_2,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    json_data = {"name": "Jane Smith"}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers, json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_update_employee_unauthorized_without_token(
    http_client: AsyncClient,
    session: AsyncSession,
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 9000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=90, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    json_data = {"role": ShopRole.MANAGER.value}

    response = await http_client.patch(
        url=f"{BASE_URL}/{employee_user_id}", json=json_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_employee_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 10000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=100, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the employee was deleted from database
    await session.flush()
    result = await session.execute(
        select(ShopMembership).where(
            ShopMembership.user_id == employee_user_id
        )
    )
    assert result.first() is None


@pytest.mark.asyncio()
async def test_delete_employee_denied_for_manager(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    manager_telegram_id = 11000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=manager_telegram_id, role=ShopRole.MANAGER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=110, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(manager_telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_employee_denied_for_courier(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    courier_telegram_id = 12000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=courier_telegram_id, role=ShopRole.COURIER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=120, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(courier_telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_employee_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    owner_telegram_id = 13000
    await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    non_existent_user_id = UserId(uuid.uuid4())

    response = await http_client.delete(
        url=f"{BASE_URL}/{non_existent_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_employee_from_different_shop_denied(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 14000
    _, _ = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create employee in a different shop
    shop_id_2 = await create_shop(name="Another Shop")
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=140, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id_2,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    response = await http_client.delete(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_delete_employee_unauthorized_without_token(
    http_client: AsyncClient,
    session: AsyncSession,
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 15000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    courier_role_id = await create_role(role_id=150, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="John Doe",
    )
    await session.commit()

    response = await http_client.delete(url=f"{BASE_URL}/{employee_user_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_employee_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 16000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=160, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/{employee_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == str(employee_user_id)
    assert data["full_name"] == "John Doe"
    assert data["role"] == ShopRole.MANAGER.value


@pytest.mark.asyncio()
async def test_get_employee_not_found(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
) -> None:
    owner_telegram_id = 17000
    await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)
    non_existent_user_id = UserId(uuid.uuid4())

    response = await http_client.get(
        url=f"{BASE_URL}/{non_existent_user_id}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_employee_unauthorized_without_token(
    http_client: AsyncClient,
    session: AsyncSession,
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 18000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create an employee
    employee_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee_user_id)
    manager_role_id = await create_role(role_id=180, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="John Doe",
    )
    await session.commit()

    response = await http_client.get(url=f"{BASE_URL}/{employee_user_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio()
async def test_get_all_employees_successfully(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 19000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create multiple employees
    employee1_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee1_user_id)
    manager_role_id = await create_role(role_id=190, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee1_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="Alice Smith",
    )

    employee2_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee2_user_id)
    courier_role_id = await create_role(role_id=191, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee2_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="Bob Johnson",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    response = await http_client.get(url=f"{BASE_URL}/all", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3  # Owner + 2 employees
    names = [emp["full_name"] for emp in data]
    assert "Alice Smith" in names
    assert "Bob Johnson" in names


@pytest.mark.asyncio()
async def test_get_all_employees_filter_by_name(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 20000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create multiple employees
    employee1_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee1_user_id)
    manager_role_id = await create_role(role_id=200, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee1_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="Alice Smith",
    )

    employee2_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee2_user_id)
    courier_role_id = await create_role(role_id=201, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee2_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="Bob Johnson",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"name": "Alice"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Alice Smith"


@pytest.mark.asyncio()
async def test_get_all_employees_with_pagination(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 21000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create multiple employees
    employee1_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee1_user_id)
    manager_role_id = await create_role(role_id=210, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee1_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="Alice Smith",
    )

    employee2_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee2_user_id)
    courier_role_id = await create_role(role_id=211, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee2_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="Bob Johnson",
    )

    employee3_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee3_user_id)
    await create_shop_membership(
        user_id=employee3_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="Charlie Brown",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    # Test with limit and offset
    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=headers,
        params={"limit": 2, "offset": 1},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio()
async def test_get_all_employees_with_order(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    create_user,
    create_shop_membership,
    create_role,
) -> None:
    owner_telegram_id = 22000
    _, shop_id = await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )

    # Create multiple employees
    employee1_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee1_user_id)
    manager_role_id = await create_role(role_id=220, name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=employee1_user_id,
        shop_id=shop_id,
        role_id=manager_role_id,
        name="Alice Smith",
    )

    employee2_user_id = UserId(uuid.uuid4())
    await create_user(user_id=employee2_user_id)
    courier_role_id = await create_role(role_id=221, name=ShopRole.COURIER)
    await create_shop_membership(
        user_id=employee2_user_id,
        shop_id=shop_id,
        role_id=courier_role_id,
        name="Charlie Brown",
    )
    await session.commit()

    headers = customer_headers(owner_telegram_id)

    # Test DESC order
    response = await http_client.get(
        url=f"{BASE_URL}/all", headers=headers, params={"order": "DESC"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should be sorted by name in descending order
    assert data[0]["full_name"] > data[1]["full_name"]


@pytest.mark.asyncio()
async def test_get_all_employees_unauthorized_without_token(
    http_client: AsyncClient,
    session: AsyncSession,
    setup_full_test_user_with_shop,
) -> None:
    owner_telegram_id = 23000
    await setup_full_test_user_with_shop(
        telegram_id=owner_telegram_id, role=ShopRole.OWNER
    )
    await session.commit()

    response = await http_client.get(url=f"{BASE_URL}/all")

    assert response.status_code == status.HTTP_403_FORBIDDEN
