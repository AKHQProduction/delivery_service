import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.infrastructure.persistence.gateways import (
    RedisLinkGateway,
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


@pytest_asyncio.fixture()
async def link_gateway(redis_client: Redis) -> RedisLinkGateway:
    return RedisLinkGateway(redis=redis_client)
