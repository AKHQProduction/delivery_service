import uuid
from datetime import date
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.commands.run_recurring_order_automation import (
    RunRecurringOrderAutomationCommand,
    RunRecurringOrderAutomationCommandHandler,
)
from backend.application.services.order_intake import OrderIntake
from backend.application.services.recurring.execution import (
    RecurringOrderExecution,
)
from backend.application.services.recurring.occurrence_ledger import (
    RecurringOrderOccurrenceLedger,
)
from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.services.recurring.template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import (
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyRecurringOrderGateway,
    SQLAlchemyRouteEdgeHistoryGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
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
from backend.infrastructure.transaction_manager import TransactionManager


class _NoopGeocoder:
    async def geocode_if_missing(self, **_: Any) -> None:
        return None


class _NoopRouteOptimizer:
    async def compute(self, *_: Any, **__: Any) -> None:
        return None


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


def _automation(
    session: AsyncSession,
) -> RunRecurringOrderAutomationCommandHandler:
    recurring_order_gateway = SQLAlchemyRecurringOrderGateway(session)
    order_intake = OrderIntake(
        client_gateway=SQLAlchemyClientGateway(session),
        product_gateway=SQLAlchemyProductGateway(session),
        order_gateway=SQLAlchemyOrderGateway(session),
        time_slot_gateway=SQLAlchemyTimeSlotGateway(session),
        shop_gateway=SQLAlchemyShopGateway(session),
        route_plan_gateway=SQLAlchemyRoutePlanGateway(session),
        route_edge_history_gateway=SQLAlchemyRouteEdgeHistoryGateway(session),
        route_optimizer=_NoopRouteOptimizer(),
        geocoder=_NoopGeocoder(),
    )
    occurrence_ledger = RecurringOrderOccurrenceLedger(recurring_order_gateway)
    execution = RecurringOrderExecution(
        recurring_order_gateway=recurring_order_gateway,
        order_intake=order_intake,
        occurrence_ledger=occurrence_ledger,
        scheduling_clock=RecurringOrderSchedulingClock(),
        template_integrity=RecurringOrderTemplateIntegrity(
            client_gateway=SQLAlchemyClientGateway(session),
            time_slot_gateway=SQLAlchemyTimeSlotGateway(session),
            product_gateway=SQLAlchemyProductGateway(session),
        ),
    )
    return RunRecurringOrderAutomationCommandHandler(
        recurring_order_gateway=recurring_order_gateway,
        recurring_order_execution=execution,
        tr_manager=TransactionManager(session),
    )


async def _create_recurring_order(
    session: AsyncSession,
    *,
    shop_id: ShopId,
    client_id: uuid.UUID,
    phone_id: int,
    address_id: int,
    time_slot_id: uuid.UUID | None,
    product_id: uuid.UUID,
    status: RecurringOrderStatus = RecurringOrderStatus.ACTIVE,
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
        status=status,
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
async def test_daily_automation_processes_active_templates_from_tomorrow(
    session: AsyncSession,
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 10),
    )
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=9200)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    active_id = await _create_recurring_order(
        session,
        shop_id=shop_id,
        client_id=client_id,
        phone_id=phone_id,
        address_id=address_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
    )
    await _create_recurring_order(
        session,
        shop_id=shop_id,
        client_id=client_id,
        phone_id=phone_id,
        address_id=address_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
        status=RecurringOrderStatus.PAUSED,
    )
    await session.flush()

    await _automation(session).handle(RunRecurringOrderAutomationCommand())
    await session.flush()

    orders = (
        await session.execute(
            select(Order)
            .where(Order.recurring_order_id == active_id)
            .order_by(Order.date)
        )
    ).scalars()
    assert [order.date for order in orders] == [
        date(2026, 5, day) for day in range(11, 25)
    ]


@pytest.mark.asyncio()
async def test_daily_automation_pauses_invalid_template_and_continues(
    session: AsyncSession,
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 10),
    )
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=9201)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    product_id, _, _, _ = await setup_test_product(shop_id=shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    time_slot_id = await _time_slot_id(session, shop_id)
    invalid_id = await _create_recurring_order(
        session,
        shop_id=shop_id,
        client_id=client_id,
        phone_id=phone_id,
        address_id=address_id,
        time_slot_id=None,
        product_id=product_id,
    )
    valid_id = await _create_recurring_order(
        session,
        shop_id=shop_id,
        client_id=client_id,
        phone_id=phone_id,
        address_id=address_id,
        time_slot_id=time_slot_id,
        product_id=product_id,
    )
    await session.flush()

    await _automation(session).handle(RunRecurringOrderAutomationCommand())
    await session.flush()

    invalid = await session.get(RecurringOrder, invalid_id)
    assert invalid is not None
    assert invalid.status == RecurringOrderStatus.PAUSED
    valid_orders = (
        await session.execute(
            select(Order).where(Order.recurring_order_id == valid_id)
        )
    ).scalars()
    assert len(list(valid_orders)) == 14


@pytest.mark.asyncio()
async def test_daily_automation_is_idempotent_for_retry(
    session: AsyncSession,
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_product,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.application.services.recurring.scheduling_clock.today",
        lambda: date(2026, 5, 10),
    )
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=9202)
    client_id = await setup_test_client(
        shop_id=shop_id,
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
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

    await _automation(session).handle(RunRecurringOrderAutomationCommand())
    await session.flush()
    first_orders = (
        await session.execute(
            select(Order).where(Order.recurring_order_id == recurring_order_id)
        )
    ).scalars()
    assert len(list(first_orders)) == 14

    await _automation(session).handle(RunRecurringOrderAutomationCommand())
    await session.flush()

    orders = (
        await session.execute(
            select(Order).where(Order.recurring_order_id == recurring_order_id)
        )
    ).scalars()
    assert len(list(orders)) == 14
