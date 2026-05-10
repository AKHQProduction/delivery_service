import uuid
from datetime import date

import pytest
from dishka.integrations.taskiq import setup_dishka
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import InMemoryBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from backend.application.vars import (
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
)
from backend.bootstrap.config import Config
from backend.infrastructure.persistence.tables.clients import (
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)
from backend.infrastructure.tasks import setup_tasks


async def _client_refs(
    session: AsyncSession, client_id: uuid.UUID
) -> tuple[int, int]:
    phone_result = await session.execute(
        select(ClientPhone.id).where(ClientPhone.client_id == client_id)
    )
    address_result = await session.execute(
        select(ClientAddress.id).where(ClientAddress.client_id == client_id)
    )
    return phone_result.scalar_one(), address_result.scalar_one()


async def _time_slot_id(session: AsyncSession, shop_id: ShopId) -> uuid.UUID:
    result = await session.execute(
        select(ShopDeliveryTimeSlot.id).where(
            ShopDeliveryTimeSlot.shop_id == shop_id
        )
    )
    time_slot_id = result.scalars().first()
    assert time_slot_id is not None
    return time_slot_id


async def _create_recurring_order(
    session: AsyncSession,
    *,
    shop_id: ShopId,
    client_id: uuid.UUID,
    phone_id: int,
    address_id: int,
    time_slot_id: uuid.UUID,
    product_id: uuid.UUID,
) -> uuid.UUID:
    recurring_order_id = uuid.uuid4()
    recurring_order = RecurringOrder(
        id=recurring_order_id,
        shop_id=shop_id,
        client_id=client_id,
        address_id=address_id,
        phone_id=phone_id,
        time_slot_id=time_slot_id,
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1, 2, 3, 4, 5, 6, 7],
        month_days=None,
        payment_method="Готівка",
        status=RecurringOrderStatus.ACTIVE,
    )
    recurring_order.items = [
        RecurringOrderItem(
            recurring_order_id=recurring_order_id,
            product_id=product_id,
            quantity=1,
        )
    ]
    session.add(recurring_order)
    return recurring_order_id


@pytest.mark.asyncio()
async def test_recurring_order_task_registered_in_memory_scheduler() -> None:
    broker = InMemoryBroker()
    setup_tasks(broker)
    source = LabelScheduleSource(broker)
    scheduler = TaskiqScheduler(broker, sources=[source])

    await scheduler.startup()
    try:
        await source.startup()
        schedules = await source.get_schedules()
    finally:
        await source.shutdown()
        await scheduler.shutdown()

    assert len(schedules) == 1
    schedule = schedules[0]
    assert schedule.task_name == "generate_recurring_orders"
    assert schedule.schedule_id == "daily-recurring-order-generation"
    assert schedule.cron == "0 0 * * *"
    assert schedule.cron_offset == "Europe/Kyiv"
    assert schedule.labels["retry_on_error"] is True
    assert schedule.labels["max_retries"] == 3


@pytest.mark.asyncio()
async def test_recurring_order_task_executes_with_real_database(
    session: AsyncSession,
    make_container,
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 10),
    )
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=9203)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[
            {
                "street": "Хрещатик",
                "house": "10",
                "latitude": 50.4501,
                "longitude": 30.5234,
            }
        ],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    recurring_order_id = await _create_recurring_order(
        session,
        shop_id=shop_id,
        client_id=client_id,
        phone_id=phone_id,
        address_id=address_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
    )
    await session.flush()

    container = make_container(Config())
    broker = InMemoryBroker(await_inplace=True)
    setup_tasks(broker)
    setup_dishka(container, broker)

    await broker.startup()
    try:
        task = broker.get_all_tasks()["generate_recurring_orders"]
        await task.kiq()
        await broker.wait_all()
    finally:
        await broker.shutdown()
        await container.close()

    await session.flush()
    orders = (
        await session.execute(
            select(Order)
            .where(Order.recurring_order_id == recurring_order_id)
            .order_by(Order.date)
        )
    ).scalars()
    assert [order.date for order in orders] == [
        date(2026, 5, day) for day in range(11, 25)
    ]
