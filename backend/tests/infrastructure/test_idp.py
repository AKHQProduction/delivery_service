import uuid

import pytest
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.vars import UserId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway
from backend.infrastructure.persistence.tables import TelegramAccount, User

TELEGRAM_ID = 1488


@pytest_asyncio.fixture()
async def idp(user_gateway: SQLAlchemyUserGateway) -> TelegramIdentityProvider:
    return TelegramIdentityProvider(
        telegram_id=TELEGRAM_ID, user_gateway=user_gateway
    )


@pytest.mark.asyncio()
async def test_idp_return_user_id_if_user_exists(
    session: AsyncSession, idp: TelegramIdentityProvider
) -> None:
    user_id = UserId(uuid.uuid4())
    await session.execute(
        insert(User).values(
            id=user_id,
        )
    )
    await session.execute(
        insert(TelegramAccount).values(
            user_id=user_id, telegram_id=TELEGRAM_ID, full_name="TestUser"
        )
    )

    current_user_id = await idp.current_user_id()

    assert current_user_id == user_id


@pytest.mark.asyncio()
async def test_idp_return_none_if_user_not_exists(
    idp: TelegramIdentityProvider,
) -> None:
    current_user_id = await idp.current_user_id()

    assert current_user_id is None
