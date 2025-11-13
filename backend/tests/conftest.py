import os
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dishka import (
    AnyOf,
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from dotenv import load_dotenv
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application.interfaces import TransactionManager
from backend.application.vars import ShopId, ShopRole, UserId
from backend.bootstrap.config import Config, PostgresConfig
from backend.bootstrap.entrypoints.di.common import PersistenceProvider
from backend.bootstrap.entrypoints.di.tests_providers import (
    MockConfigProvider,
    MockWebAppProvider,
)
from backend.infrastructure.persistence.tables import (
    Base,
    Role,
    Shop,
    ShopMembership,
    TelegramAccount,
    User,
)


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


@pytest.fixture()
def mock_session_provider(session: AsyncSession) -> Provider:
    class MockPersistenceProvider(PersistenceProvider):
        @provide(
            scope=Scope.REQUEST,
            provides=AnyOf[AsyncSession, TransactionManager],
        )
        async def get_session(self) -> AsyncSession:
            return session

    return MockPersistenceProvider()


@pytest.fixture()
def make_container(
    postgres_config: PostgresConfig,
    mock_session_provider: Provider,
) -> Callable[[Config], AsyncContainer]:
    def _container(config: Config) -> AsyncContainer:
        config.postgres_config = postgres_config

        return make_async_container(
            mock_session_provider,
            MockConfigProvider(),
            MockWebAppProvider(),
            context={Config: config},
        )

    return _container


@pytest.fixture()
def create_role(session: AsyncSession):
    async def _create_role(
        role_id: int = 1,
        name: ShopRole = ShopRole.OWNER,
    ) -> int:
        await session.execute(insert(Role).values(id=role_id, name=name.value))
        return role_id

    return _create_role


@pytest.fixture()
def create_user(session: AsyncSession):
    async def _create_user(
        user_id: UserId | None = None,
    ) -> UserId:
        if user_id is None:
            user_id = UserId(uuid.uuid4())
        await session.execute(insert(User).values(id=user_id))
        return user_id

    return _create_user


@pytest.fixture()
def create_telegram_account(session: AsyncSession):
    async def _create_telegram_account(
        user_id: UserId, telegram_id: int, full_name: str = "Test User"
    ) -> None:
        await session.execute(
            insert(TelegramAccount).values(
                user_id=user_id, telegram_id=telegram_id, full_name=full_name
            )
        )

    return _create_telegram_account


@pytest.fixture()
def create_shop(session: AsyncSession):
    async def _create_shop(
        shop_id: ShopId | None = None,
        name: str = "Test Shop",
    ) -> ShopId:
        if shop_id is None:
            shop_id = ShopId(uuid.uuid4())
        await session.execute(insert(Shop).values(id=shop_id, name=name))
        return shop_id

    return _create_shop


@pytest.fixture()
def create_shop_membership(session: AsyncSession):
    async def _create_shop_membership(
        user_id: UserId,
        shop_id: ShopId,
        role_id: int = 1,
    ) -> None:
        await session.execute(
            insert(ShopMembership).values(
                user_id=user_id, shop_id=shop_id, role_id=role_id
            )
        )

    return _create_shop_membership


@pytest.fixture()
def setup_full_test_user_with_shop(
    create_user,
    create_telegram_account,
    create_shop,
    create_role,
    create_shop_membership,
):
    async def _setup_user(
        telegram_id: int,
        full_name: str = "Test User",
        user_id: UserId | None = None,
        role: ShopRole = ShopRole.OWNER,
    ) -> UserId:
        user_id = await create_user(user_id=user_id)
        await create_telegram_account(
            user_id=user_id, telegram_id=telegram_id, full_name=full_name
        )
        role_id = await create_role(name=role)
        shop_id = await create_shop()
        await create_shop_membership(
            user_id=user_id, shop_id=shop_id, role_id=role_id
        )
        return user_id

    return _setup_user
