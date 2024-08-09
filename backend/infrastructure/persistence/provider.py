import logging
from typing import AsyncGenerator, AsyncIterable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infrastructure.persistence.config import DBConfig


async def get_engine(settings: DBConfig) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        settings.get_connection_url(),
        future=True,
    )

    logging.info("Engine was created.")

    yield engine

    await engine.dispose()

    logging.info("Engine was disposed.")


async def get_async_sessionmaker(
        engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    logging.info("Session provider was initialized")

    return session_factory


async def get_async_session(
        session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterable[AsyncSession]:
    async with session_factory() as session:
        yield session
