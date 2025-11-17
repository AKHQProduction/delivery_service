import uuid
from typing import TYPE_CHECKING

import pytest
from faker import Faker
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import AuthorizationError
from backend.application.vars import ShopRole, UserId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.persistence.tables import TelegramAccount, User

if TYPE_CHECKING:
    from backend.application.interfaces.idp import CurrentUserDTO

TELEGRAM_ID = 1488


@pytest.fixture()
def idp(
    user_gateway: SQLAlchemyUserGateway, shop_gateway: SQLAlchemyShopGateway
):
    def _idp(telegram_id: int = 1488) -> TelegramIdentityProvider:
        return TelegramIdentityProvider(
            telegram_id=telegram_id,
            user_gateway=user_gateway,
            shop_gateway=shop_gateway,
        )

    return _idp


@pytest.mark.asyncio()
async def test_idp_return_user_id_if_user_exists(
    session: AsyncSession, idp
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

    telegram_idp = idp(telegram_id=TELEGRAM_ID)
    current_user_id = await telegram_idp.current_user_id()

    assert current_user_id == user_id


@pytest.mark.asyncio()
async def test_idp_return_none_if_user_not_exists(
    idp,
) -> None:
    telegram_idp = idp()
    current_user_id = await telegram_idp.current_user_id()

    assert current_user_id is None


@pytest.mark.asyncio()
async def test_return_correct_user_data(
    idp, faker: Faker, setup_full_test_user_with_shop
) -> None:
    telegram_id = faker.random_int()
    role = faker.random_element([
        ShopRole.OWNER,
        ShopRole.MANAGER,
        ShopRole.COURIER,
    ])
    user_id, _ = await setup_full_test_user_with_shop(
        telegram_id=telegram_id, role=role
    )

    telegram_idp = idp(telegram_id=telegram_id)
    current_user: CurrentUserDTO = await telegram_idp.current_user()

    assert current_user.user_id == user_id
    assert current_user.role == role


@pytest.mark.asyncio()
async def test_raise_authorize_error_when_user_not_exists(idp) -> None:
    telegram_idp = idp()

    with pytest.raises(AuthorizationError):
        await telegram_idp.current_user()
