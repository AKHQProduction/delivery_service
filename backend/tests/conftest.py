import os
import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.application.vars import (
    CategoryId,
    ClientId,
    DistrictId,
    OrderId,
    PaymentMethodId,
    ProductId,
    ShopId,
    ShopRole,
    TimeSlotId,
    UserId,
)
from backend.bootstrap.config import Config, PostgresConfig, RedisConfig
from backend.bootstrap.entrypoints.di.common import (
    PersistenceProvider,
    RedisProvider,
)
from backend.bootstrap.entrypoints.di.tests_providers import (
    MockAPIInteractorsProvider,
    MockAdaptersProvider,
    MockAuthProvider,
    MockConfigProvider,
    MockGeocoderProvider,
    MockServicesProvider,
)
from backend.infrastructure.persistence.tables import (
    Base,
    Category,
    District,
    Product,
    Role,
    Shop,
    ShopMembership,
    TelegramAccount,
    User,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.orders import Order, OrderItem
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
    ShopPaymentMethod,
)


@pytest.fixture(scope="session")
def redis_config() -> RedisConfig:
    load_dotenv()

    return RedisConfig(
        REDIS_HOST=cast("str", os.getenv("TEST_REDIS_HOST")),
        REDIS_PORT=int(cast("str", os.getenv("TEST_REDIS_PORT"))),
        REDIS_PASSWORD=cast("str", os.getenv("TEST_REDIS_PASSWORD")),
    )


@pytest_asyncio.fixture()
async def redis_client(
    redis_config: RedisConfig,
) -> AsyncGenerator[Redis, None]:
    async with Redis.from_url(redis_config.persistence_uri) as redis:
        yield redis

        # Cleanup
        await redis.flushdb()


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
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AsyncSession:
            return session

    return MockPersistenceProvider()


@pytest.fixture()
def make_container(
    postgres_config: PostgresConfig,
    redis_config: RedisConfig,
    mock_session_provider: Provider,
) -> Callable[[Config], AsyncContainer]:
    def _container(config: Config) -> AsyncContainer:
        config.postgres_config = postgres_config
        config.redis_config = redis_config

        return make_async_container(
            mock_session_provider,
            MockConfigProvider(),
            MockAuthProvider(),
            MockAPIInteractorsProvider(),
            MockAdaptersProvider(),
            MockServicesProvider(),
            MockGeocoderProvider(),
            RedisProvider(),
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
        city: str | None = None,
        street: str | None = None,
        house: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> ShopId:
        if shop_id is None:
            shop_id = ShopId(uuid.uuid4())
        await session.execute(
            insert(Shop).values(
                id=shop_id,
                name=name,
                city=city,
                street=street,
                house=house,
                latitude=latitude,
                longitude=longitude,
            )
        )
        return shop_id

    return _create_shop


@pytest.fixture()
def create_shop_membership(session: AsyncSession):
    async def _create_shop_membership(
        user_id: UserId,
        shop_id: ShopId,
        role_id: int = 1,
        name: str = "Test User",
    ) -> None:
        await session.execute(
            insert(ShopMembership).values(
                user_id=user_id, shop_id=shop_id, role_id=role_id, name=name
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
    setup_test_time_slot,
    setup_test_payment_method,
):
    async def _setup_user(
        telegram_id: int,
        full_name: str = "Test User",
        user_id: UserId | None = None,
        role: ShopRole = ShopRole.OWNER,
        shop_city: str | None = None,
        shop_street: str | None = None,
        shop_house: str | None = None,
        shop_latitude: float | None = None,
        shop_longitude: float | None = None,
    ) -> tuple[UserId, ShopId]:
        user_id = await create_user(user_id=user_id)
        await create_telegram_account(
            user_id=user_id, telegram_id=telegram_id, full_name=full_name
        )
        role_id = await create_role(name=role)
        shop_id = await create_shop(
            city=shop_city,
            street=shop_street,
            house=shop_house,
            latitude=shop_latitude,
            longitude=shop_longitude,
        )
        await create_shop_membership(
            user_id=user_id, shop_id=shop_id, role_id=role_id
        )
        await setup_test_time_slot(
            shop_id=shop_id,
            start_time=time(9, 0),
            end_time=time(14, 0),
            label="Перша половина дня",
        )
        await setup_test_time_slot(
            shop_id=shop_id,
            start_time=time(14, 0),
            end_time=time(21, 0),
            label="Друга половина дня",
        )
        await setup_test_payment_method(shop_id=shop_id, name="Готівка")
        await setup_test_payment_method(shop_id=shop_id, name="На рахунок")
        await setup_test_payment_method(shop_id=shop_id, name="Інше")
        await setup_test_payment_method(shop_id=shop_id, name="Баланс")
        return user_id, shop_id

    return _setup_user


@pytest.fixture()
def setup_test_category(session: AsyncSession):
    async def _setup_test_category(
        shop_id: ShopId,
        name: str = "Test Category",
        category_id: CategoryId | None = None,
    ) -> CategoryId:
        if category_id is None:
            category_id = CategoryId(uuid.uuid4())

        await session.execute(
            insert(Category).values(
                id=category_id,
                name=name,
                shop_id=shop_id,
            )
        )

        return category_id

    return _setup_test_category


@pytest.fixture()
def setup_test_district(session: AsyncSession):
    async def _setup_test_district(
        shop_id: ShopId,
        name: str = "Test District",
        district_id: DistrictId | None = None,
    ) -> DistrictId:
        if district_id is None:
            district_id = DistrictId(uuid.uuid4())

        await session.execute(
            insert(District).values(
                id=district_id,
                name=name,
                shop_id=shop_id,
            )
        )

        return district_id

    return _setup_test_district


@pytest.fixture()
def setup_test_product(session: AsyncSession):
    async def _setup_test_product(
        shop_id: ShopId,
        category_id: CategoryId | None = None,
    ) -> tuple[ProductId, str, Decimal, CategoryId | None]:
        product_id = ProductId(uuid.uuid4())
        name = "Test Product"
        price = Decimal(100)

        await session.execute(
            insert(Product).values(
                id=product_id,
                name=name,
                price=price,
                category_id=category_id,
                shop_id=shop_id,
            )
        )

        return product_id, name, price, category_id

    return _setup_test_product


@pytest.fixture()
def setup_test_client(session: AsyncSession):
    async def _setup_test_client(
        shop_id: ShopId,
        full_name: str = "Test Client",
        phones: list[str] | None = None,
        addresses: list[dict[str, Any]] | None = None,
        balance: Decimal = Decimal(0),
    ) -> ClientId:
        client_id = ClientId(uuid.uuid4())

        await session.execute(
            insert(Client).values(
                id=client_id,
                full_name=full_name,
                balance=balance,
                shop_id=shop_id,
            )
        )

        if phones:
            for idx, phone_number in enumerate(phones):
                await session.execute(
                    insert(ClientPhone).values(
                        number=phone_number,
                        is_primary=(idx == 0),
                        client_id=client_id,
                        shop_id=shop_id,
                    )
                )

        if addresses:
            for idx, address in enumerate(addresses):
                await session.execute(
                    insert(ClientAddress).values(
                        street=address["street"],
                        house=address["house"],
                        comment=address.get("comment"),
                        apartment=address.get("apartment"),
                        entrance=address.get("entrance"),
                        floor=address.get("floor"),
                        intercom=address.get("intercom"),
                        latitude=address.get("latitude"),
                        longitude=address.get("longitude"),
                        district_id=address.get("district_id"),
                        is_primary=(idx == 0),
                        client_id=client_id,
                    )
                )

        return client_id

    return _setup_test_client


@pytest.fixture()
def setup_test_time_slot(session: AsyncSession):
    async def _setup_test_time_slot(
        shop_id: ShopId,
        time_slot_id: TimeSlotId | None = None,
        start_time: time = time(6, 0),
        end_time: time = time(9, 0),
        label: str | None = "Тестовий слот",
    ) -> TimeSlotId:
        if time_slot_id is None:
            time_slot_id = TimeSlotId(uuid.uuid4())

        await session.execute(
            insert(ShopDeliveryTimeSlot).values(
                id=time_slot_id,
                shop_id=shop_id,
                start_time=start_time,
                end_time=end_time,
                label=label,
            )
        )

        return time_slot_id

    return _setup_test_time_slot


@pytest.fixture()
def setup_test_payment_method(session: AsyncSession):
    async def _setup_test_payment_method(
        shop_id: ShopId,
        payment_method_id: PaymentMethodId | None = None,
        name: str = "Тестовий метод",
    ) -> PaymentMethodId:
        if payment_method_id is None:
            payment_method_id = PaymentMethodId(uuid.uuid4())

        await session.execute(
            insert(ShopPaymentMethod).values(
                id=payment_method_id,
                shop_id=shop_id,
                name=name,
            )
        )

        return payment_method_id

    return _setup_test_payment_method


@pytest.fixture()
def setup_test_order(session: AsyncSession):
    async def _setup_test_order(
        shop_id: ShopId,
        client_id: ClientId,
        order_id: OrderId | None = None,
        delivery_date: datetime | None = None,
        delivery_start_time: time = time(9, 0),
        delivery_end_time: time = time(14, 0),
        delivery_phone: str = "+380501234567",
        delivery_address: dict[str, Any] | None = None,
        comment: str | None = None,
        items: list[dict[str, Any]] | None = None,
        is_paid: bool = False,
        payment_method: str = "OTHER",
    ) -> OrderId:
        if order_id is None:
            order_id = OrderId(uuid.uuid4())
        if delivery_date is None:
            delivery_date = datetime.now(UTC).date() + timedelta(days=1)
        if delivery_address is None:
            delivery_address = {
                "street": "Test Street",
                "house": "1",
                "apartment": "5",
            }

        await session.execute(
            insert(Order).values(
                id=order_id,
                date=delivery_date,
                delivery_address=delivery_address,
                delivery_phone=delivery_phone,
                delivery_start_time=delivery_start_time,
                delivery_end_time=delivery_end_time,
                comment=comment,
                shop_id=shop_id,
                client_id=client_id,
                is_paid=is_paid,
                payment_method=payment_method,
            )
        )

        if items is None:
            items = [
                {
                    "name": "Test Product",
                    "quantity": 1,
                    "price_per_item": Decimal(100),
                }
            ]

        for item in items:
            await session.execute(
                insert(OrderItem).values(
                    name=item["name"],
                    quantity=item["quantity"],
                    price_per_item=item["price_per_item"],
                    order_id=order_id,
                )
            )

        return order_id

    return _setup_test_order
