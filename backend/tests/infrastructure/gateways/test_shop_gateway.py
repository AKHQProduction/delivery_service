import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
)
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
)
from backend.infrastructure.persistence.tables import Shop


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
