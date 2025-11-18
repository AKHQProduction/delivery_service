import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.infrastructure.persistence.gateways import (
    SQLAlchemyProductGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)


@pytest_asyncio.fixture()
async def user_gateway(session: AsyncSession) -> SQLAlchemyUserGateway:
    return SQLAlchemyUserGateway(session=session)


@pytest_asyncio.fixture()
async def shop_gateway(session: AsyncSession) -> SQLAlchemyShopGateway:
    return SQLAlchemyShopGateway(session=session)


@pytest_asyncio.fixture()
async def product_gateway(session: AsyncSession) -> SQLAlchemyProductGateway:
    return SQLAlchemyProductGateway(session=session)
