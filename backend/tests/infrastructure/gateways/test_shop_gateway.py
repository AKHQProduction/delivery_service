import uuid

import pytest
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
)
from backend.infrastructure.persistence.tables import (
    Role,
    Shop,
    ShopMembership,
    User,
)


@pytest_asyncio.fixture()
async def shop_gateway(session: AsyncSession) -> SQLAlchemyShopGateway:
    return SQLAlchemyShopGateway(session=session)


@pytest.mark.asyncio()
async def test_return_false_when_membership_not_exists(
    shop_gateway: SQLAlchemyShopGateway,
) -> None:
    user_id = UserId(uuid.uuid4())
    result = await shop_gateway.relate_to_shop(user_id)

    assert result is False


@pytest.mark.asyncio()
async def test_return_true_when_membership_exists(
    session: AsyncSession, shop_gateway: SQLAlchemyShopGateway
) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    role_id = 1

    await session.execute(insert(Role).values(id=role_id, name=ShopRole.OWNER))
    await session.execute(insert(User).values(id=user_id))
    await session.execute(insert(Shop).values(id=shop_id, name="Test Shop"))
    await session.execute(
        insert(ShopMembership).values(
            user_id=user_id, shop_id=shop_id, role_id=role_id
        )
    )
    await session.flush()

    result = await shop_gateway.relate_to_shop(user_id)

    assert result is True
