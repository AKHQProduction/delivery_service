import os
from collections.abc import AsyncGenerator
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.bootstrap.config import PostgresConfig
from backend.infrastructure.persistence.gateways import SQLAlchemyUserGateway
from backend.infrastructure.persistence.tables import Base


@pytest.fixture(scope="session")
def postgres_config() -> PostgresConfig:
    load_dotenv()

    return PostgresConfig(
        POSTGRES_USER=cast("str", os.getenv("TEST_POSTGRES_USER")),
        POSTGRES_DB=cast("str", os.getenv("TEST_POSTGRES_DB")),
        POSTGRES_PORT=int(cast("str", os.getenv("TEST_POSTGRES_PORT"))),
        POSTGRES_PASSWORD=cast("str", os.getenv("TEST_POSTGRES_PASSWORD")),
        DB_HOST=cast("str", os.getenv("TEST_DB_HOST")),
    )


@pytest_asyncio.fixture(scope="session")
async def session_maker(
    postgres_config: PostgresConfig,
) -> async_sessionmaker[AsyncSession]:
    database_uri = (
        f"postgresql+psycopg://{postgres_config.user}:{postgres_config.password}"
        f"@{postgres_config.host}:{postgres_config.port}/{postgres_config.db_name}"
    )

    engine = create_async_engine(database_uri)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture()
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any]:
    async with session_maker() as session:
        session.commit = AsyncMock()  # type: ignore[method-assign]
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def user_gateway(session: AsyncSession) -> SQLAlchemyUserGateway:
    return SQLAlchemyUserGateway(session=session)
