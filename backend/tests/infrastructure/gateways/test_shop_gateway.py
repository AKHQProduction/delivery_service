import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
    ShopEmployee,
)
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
)
from backend.infrastructure.persistence.tables import Shop, ShopMembership


@pytest.mark.asyncio()
async def test_return_false_when_membership_not_exists(
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    result = await shop_gateway.relate_to_shop(user_id)

    assert result is False


@pytest.mark.asyncio()
async def test_return_true_when_membership_exists(
    session: AsyncSession,
    shop_gateway: SQLAlchemyShopGateway,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    role_id = 1

    await create_role(role_id=role_id)
    await create_user(user_id=user_id)
    await create_shop(shop_id=shop_id)
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id
    )
    await session.flush()

    result = await shop_gateway.relate_to_shop(user_id)

    assert result is True


@pytest.mark.asyncio()
async def test_save_new_shop(
    shop_gateway: SQLAlchemyShopGateway,
    session: AsyncSession,
    create_role,
    create_user,
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    role_id = 1

    await create_role(role_id=role_id)
    await create_user(user_id=user_id)
    await session.flush()

    shop_dto = CreateNewShopDTO(
        shop_id=shop_id,
        user_id=user_id,
        shop_name="Test Shop",
        owner_name="Test User",
    )

    await shop_gateway.create_shop(shop_dto)
    await session.flush()

    result = await session.execute(
        select(Shop).where(Shop.id == shop_dto.shop_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    shop = rows[0][0]
    assert shop.name == shop_dto.shop_name


def test_return_shop_id(shop_gateway: SQLAlchemyShopGateway) -> None:
    result = shop_gateway.next_id()

    assert isinstance(result, uuid.UUID)
    assert result.version == 7


def test_return_unique_shop_ids(shop_gateway: SQLAlchemyShopGateway) -> None:
    id1 = shop_gateway.next_id()
    id2 = shop_gateway.next_id()
    id3 = shop_gateway.next_id()

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3
    assert all(isinstance(shop_id, uuid.UUID) for shop_id in [id1, id2, id3])


@pytest.mark.parametrize(
    "role", (ShopRole.OWNER, ShopRole.MANAGER, ShopRole.COURIER)
)
@pytest.mark.asyncio()
async def test_get_shop_employee_returns_employee_data(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    role: ShopRole,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    employee_name = "John Doe"

    role_id = await create_role(name=role)
    await create_user(user_id=user_id)
    shop_id = await create_shop()
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id, name=employee_name
    )
    await session.flush()

    result = await shop_gateway.get_shop_employee(user_id=user_id)

    assert result is not None
    assert result.user_id == user_id
    assert result.shop_id == shop_id
    assert result.role == role
    assert result.full_name == employee_name


@pytest.mark.asyncio()
async def test_get_shop_employee_returns_none_when_user_not_exists(
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())

    result = await shop_gateway.get_shop_employee(user_id=user_id)

    assert result is None


@pytest.mark.parametrize(
    "role", (ShopRole.OWNER, ShopRole.MANAGER, ShopRole.COURIER)
)
@pytest.mark.asyncio()
async def test_save_new_employee(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    shop_gateway: SQLAlchemyShopGateway,
    role: ShopRole,
) -> None:
    user_id = UserId(uuid.uuid4())
    employee_name = "John Doe"
    await create_user(user_id=user_id)
    shop_id = await create_shop()
    role_id = 1

    await create_role(role_id=role_id, name=role)
    await session.flush()

    await shop_gateway.add_employee(
        ShopEmployee(
            user_id=user_id,
            shop_id=shop_id,
            full_name=employee_name,
            role=role,
        )
    )
    await session.flush()

    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    employee: ShopMembership = rows[0][0]
    assert employee.user_id == user_id
    assert employee.name == employee_name
    assert employee.shop_id == shop_id


@pytest.mark.parametrize(
    ("initial_role", "updated_role"),
    (
        (ShopRole.MANAGER, ShopRole.COURIER),
        (ShopRole.COURIER, ShopRole.MANAGER),
        (ShopRole.OWNER, ShopRole.MANAGER),
    ),
)
@pytest.mark.asyncio()
async def test_update_employee_role_and_name(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
    initial_role: ShopRole,
    updated_role: ShopRole,
) -> None:
    user_id = UserId(uuid.uuid4())
    initial_name = "John Doe"
    updated_name = "Jane Smith"

    await create_user(user_id=user_id)
    shop_id = await create_shop()
    initial_role_id = await create_role(name=initial_role)
    updated_role_id = await create_role(
        role_id=initial_role_id + 1, name=updated_role
    )
    await create_shop_membership(
        user_id=user_id,
        shop_id=shop_id,
        role_id=initial_role_id,
        name=initial_name,
    )
    await session.flush()

    await shop_gateway.update_employee(
        ShopEmployee(
            user_id=user_id,
            shop_id=shop_id,
            full_name=updated_name,
            role=updated_role,
        )
    )
    await session.flush()

    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    employee: ShopMembership = rows[0][0]
    assert employee.user_id == user_id
    assert employee.name == updated_name
    assert employee.role_id == updated_role_id
    assert employee.shop_id == shop_id


@pytest.mark.asyncio()
async def test_update_employee_name_only(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    initial_name = "John Doe"
    updated_name = "John Smith"
    role = ShopRole.MANAGER

    await create_user(user_id=user_id)
    shop_id = await create_shop()
    role_id = await create_role(name=role)
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id, name=initial_name
    )
    await session.flush()

    await shop_gateway.update_employee(
        ShopEmployee(
            user_id=user_id,
            shop_id=shop_id,
            full_name=updated_name,
            role=role,
        )
    )
    await session.flush()

    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    employee: ShopMembership = rows[0][0]
    assert employee.name == updated_name
    assert employee.role_id == role_id


@pytest.mark.asyncio()
async def test_update_employee_role_only(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    employee_name = "John Doe"
    initial_role = ShopRole.COURIER
    updated_role = ShopRole.MANAGER

    await create_user(user_id=user_id)
    shop_id = await create_shop()
    initial_role_id = await create_role(name=initial_role)
    updated_role_id = await create_role(
        role_id=initial_role_id + 1, name=updated_role
    )
    await create_shop_membership(
        user_id=user_id,
        shop_id=shop_id,
        role_id=initial_role_id,
        name=employee_name,
    )
    await session.flush()

    await shop_gateway.update_employee(
        ShopEmployee(
            user_id=user_id,
            shop_id=shop_id,
            full_name=employee_name,
            role=updated_role,
        )
    )
    await session.flush()

    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    employee: ShopMembership = rows[0][0]
    assert employee.name == employee_name
    assert employee.role_id == updated_role_id


@pytest.mark.asyncio()
async def test_update_employee_updates_only_specific_user(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id_1 = UserId(uuid.uuid4())
    user_id_2 = UserId(uuid.uuid4())
    initial_name_1 = "John Doe"
    initial_name_2 = "Jane Smith"
    updated_name = "John Updated"
    role = ShopRole.MANAGER

    await create_user(user_id=user_id_1)
    await create_user(user_id=user_id_2)
    shop_id = await create_shop()
    role_id = await create_role(name=role)
    await create_shop_membership(
        user_id=user_id_1,
        shop_id=shop_id,
        role_id=role_id,
        name=initial_name_1,
    )
    await create_shop_membership(
        user_id=user_id_2,
        shop_id=shop_id,
        role_id=role_id,
        name=initial_name_2,
    )
    await session.flush()

    await shop_gateway.update_employee(
        ShopEmployee(
            user_id=user_id_1,
            shop_id=shop_id,
            full_name=updated_name,
            role=role,
        )
    )
    await session.flush()

    # Check first user was updated
    result_1 = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id_1)
    )
    employee_1: ShopMembership = result_1.scalar_one()
    assert employee_1.name == updated_name

    # Check second user was not affected
    result_2 = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id_2)
    )
    employee_2: ShopMembership = result_2.scalar_one()
    assert employee_2.name == initial_name_2


@pytest.mark.asyncio()
async def test_delete_employee_successfully(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    await create_user(user_id=user_id)
    shop_id = await create_shop()
    role_id = await create_role(name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id, name="John Doe"
    )
    await session.flush()

    # Verify employee exists
    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    assert result.scalar_one() is not None

    await shop_gateway.delete_employee(user_id)
    await session.flush()

    # Verify employee was deleted
    result = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id)
    )
    assert result.first() is None


@pytest.mark.asyncio()
async def test_delete_employee_does_not_affect_other_employees(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id_1 = UserId(uuid.uuid4())
    user_id_2 = UserId(uuid.uuid4())
    await create_user(user_id=user_id_1)
    await create_user(user_id=user_id_2)
    shop_id = await create_shop()
    role_id = await create_role(name=ShopRole.MANAGER)
    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id, role_id=role_id, name="John Doe"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id, role_id=role_id, name="Jane Smith"
    )
    await session.flush()

    await shop_gateway.delete_employee(user_id_1)
    await session.flush()

    # Verify first employee was deleted
    result_1 = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id_1)
    )
    assert result_1.first() is None

    # Verify second employee still exists
    result_2 = await session.execute(
        select(ShopMembership).where(ShopMembership.user_id == user_id_2)
    )
    employee_2: ShopMembership = result_2.scalar_one()
    assert employee_2.name == "Jane Smith"


@pytest.mark.asyncio()
async def test_read_employee_returns_employee_data(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    employee_name = "John Doe"
    role = ShopRole.MANAGER

    await create_user(user_id=user_id)
    shop_id = await create_shop()
    role_id = await create_role(name=role)
    await create_shop_membership(
        user_id=user_id, shop_id=shop_id, role_id=role_id, name=employee_name
    )
    await session.flush()

    result = await shop_gateway.read_employee(user_id)

    assert result is not None
    assert result.user_id == user_id
    assert result.full_name == employee_name
    assert result.role == role


@pytest.mark.asyncio()
async def test_read_employee_returns_none_when_not_found(
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())

    result = await shop_gateway.read_employee(user_id)

    assert result is None


@pytest.mark.asyncio()
async def test_read_all_employees_returns_all_employees(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    from backend.application.interfaces.gateways import Pagination
    from backend.application.interfaces.gateways.shop_gateway import (
        EmployeeFilters,
    )

    shop_id = await create_shop()
    role_id = await create_role(name=ShopRole.MANAGER)

    user_id_1 = UserId(uuid.uuid4())
    user_id_2 = UserId(uuid.uuid4())
    user_id_3 = UserId(uuid.uuid4())

    await create_user(user_id=user_id_1)
    await create_user(user_id=user_id_2)
    await create_user(user_id=user_id_3)

    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id, role_id=role_id, name="Alice"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id, role_id=role_id, name="Bob"
    )
    await create_shop_membership(
        user_id=user_id_3, shop_id=shop_id, role_id=role_id, name="Charlie"
    )
    await session.flush()

    filters = EmployeeFilters(shop_id=shop_id)
    pagination = Pagination()

    result = await shop_gateway.read_all_employees(filters, pagination)

    assert len(result) == 3
    assert result[0].full_name == "Alice"
    assert result[1].full_name == "Bob"
    assert result[2].full_name == "Charlie"


@pytest.mark.asyncio()
async def test_read_all_employees_filters_by_name(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    from backend.application.interfaces.gateways import Pagination
    from backend.application.interfaces.gateways.shop_gateway import (
        EmployeeFilters,
    )

    shop_id = await create_shop()
    role_id = await create_role(name=ShopRole.MANAGER)

    user_id_1 = UserId(uuid.uuid4())
    user_id_2 = UserId(uuid.uuid4())
    user_id_3 = UserId(uuid.uuid4())

    await create_user(user_id=user_id_1)
    await create_user(user_id=user_id_2)
    await create_user(user_id=user_id_3)

    await create_shop_membership(
        user_id=user_id_1,
        shop_id=shop_id,
        role_id=role_id,
        name="Alice Johnson",
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id, role_id=role_id, name="Bob Smith"
    )
    await create_shop_membership(
        user_id=user_id_3,
        shop_id=shop_id,
        role_id=role_id,
        name="Charlie Johnson",
    )
    await session.flush()

    filters = EmployeeFilters(shop_id=shop_id, name="Johnson")
    pagination = Pagination()

    result = await shop_gateway.read_all_employees(filters, pagination)

    assert len(result) == 2
    assert result[0].full_name == "Alice Johnson"
    assert result[1].full_name == "Charlie Johnson"


@pytest.mark.asyncio()
async def test_read_all_employees_filters_by_shop_id(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    from backend.application.interfaces.gateways import Pagination
    from backend.application.interfaces.gateways.shop_gateway import (
        EmployeeFilters,
    )

    shop_id_1 = await create_shop(name="Shop 1")
    shop_id_2 = await create_shop(name="Shop 2")
    role_id = await create_role(name=ShopRole.MANAGER)

    user_id_1 = UserId(uuid.uuid4())
    user_id_2 = UserId(uuid.uuid4())

    await create_user(user_id=user_id_1)
    await create_user(user_id=user_id_2)

    await create_shop_membership(
        user_id=user_id_1, shop_id=shop_id_1, role_id=role_id, name="Alice"
    )
    await create_shop_membership(
        user_id=user_id_2, shop_id=shop_id_2, role_id=role_id, name="Bob"
    )
    await session.flush()

    filters = EmployeeFilters(shop_id=shop_id_1)
    pagination = Pagination()

    result = await shop_gateway.read_all_employees(filters, pagination)

    assert len(result) == 1
    assert result[0].full_name == "Alice"


@pytest.mark.asyncio()
async def test_read_all_employees_respects_pagination(
    session: AsyncSession,
    create_role,
    create_user,
    create_shop,
    create_shop_membership,
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    from backend.application.interfaces.gateways import Pagination
    from backend.application.interfaces.gateways.shop_gateway import (
        EmployeeFilters,
    )

    shop_id = await create_shop()
    role_id = await create_role(name=ShopRole.MANAGER)

    user_ids = [UserId(uuid.uuid4()) for _ in range(5)]
    names = ["Alice", "Bob", "Charlie", "David", "Eve"]

    for user_id, name in zip(user_ids, names, strict=False):
        await create_user(user_id=user_id)
        await create_shop_membership(
            user_id=user_id, shop_id=shop_id, role_id=role_id, name=name
        )
    await session.flush()

    filters = EmployeeFilters(shop_id=shop_id)
    pagination = Pagination(offset=1, limit=2)

    result = await shop_gateway.read_all_employees(filters, pagination)

    assert len(result) == 2
    assert result[0].full_name == "Bob"
    assert result[1].full_name == "Charlie"
