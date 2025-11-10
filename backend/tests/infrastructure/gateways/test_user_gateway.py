import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces import CreateUserViaTgDTO
from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway
from backend.infrastructure.persistence.tables import TelegramAccount, User


@pytest_asyncio.fixture()
async def user_gateway(session: AsyncSession) -> SQLAlchemyUserGateway:
    return SQLAlchemyUserGateway(session=session)


def test_return_user_id(user_gateway: SQLAlchemyUserGateway) -> None:
    result = user_gateway.next_id()

    assert isinstance(result, uuid.UUID)
    assert result.version == 7


def test_return_unique_shop_ids(user_gateway: SQLAlchemyUserGateway) -> None:
    id1 = user_gateway.next_id()
    id2 = user_gateway.next_id()
    id3 = user_gateway.next_id()

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3
    assert all(isinstance(shop_id, uuid.UUID) for shop_id in [id1, id2, id3])


@pytest.mark.asyncio()
async def test_save_new_user(
    user_gateway: SQLAlchemyUserGateway, session: AsyncSession
) -> None:
    user_id = UserId(uuid.uuid4())
    user_dto = CreateUserViaTgDTO(
        user_id=user_id, tg_id=1, full_name="Test User"
    )

    await user_gateway.create_user_via_tg(user_dto)
    await session.flush()

    result = await session.execute(
        select(User).where(User.id == user_dto.user_id)
    )
    rows = result.fetchall()
    assert len(rows) == 1
    user: User = rows[0][0]
    assert user.id == user_dto.user_id

    account_result = await session.execute(
        select(TelegramAccount).where(TelegramAccount.user_id == user_id)
    )
    account_rows = account_result.fetchall()
    assert len(account_rows) == 1

    account: TelegramAccount = account_rows[0][0]
    assert account.telegram_id == user_dto.tg_id
    assert account.full_name == user_dto.full_name
