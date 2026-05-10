from datetime import date
from typing import cast
from uuid import UUID

import pytest

from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import (
    RecurringOrderPausedError,
    RecurringOrderTemplateInvalidError,
)
from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.services.recurring.execution import (
    RecurringOrderExecution,
    RecurringOrderExecutionRequest,
    RecurringOrderExecutionResult,
)
from backend.application.services.recurring.lifecycle import (
    RecurringOrderLifecycle,
)
from backend.application.services.recurring.scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.services.recurring.template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import (
    ClientId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    ShopRole,
    TimeSlotId,
    UserId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)
from backend.infrastructure.transaction_manager import TransactionManager

SHOP_ID = ShopId(UUID("11111111-1111-1111-1111-111111111111"))
CLIENT_ID = ClientId(UUID("22222222-2222-2222-2222-222222222222"))
TIME_SLOT_ID = TimeSlotId(UUID("33333333-3333-3333-3333-333333333333"))
RECURRING_ORDER_ID = RecurringOrderId(
    UUID("44444444-4444-4444-4444-444444444444")
)
TODAY = date(2026, 5, 10)
FUTURE_CUTOFF = date(2026, 5, 11)


class FakeRecurringOrderGateway:
    def __init__(self) -> None:
        self.deleted: list[RecurringOrder] = []

    async def delete(self, recurring_order: RecurringOrder) -> None:
        self.deleted.append(recurring_order)


class FakeGeneratedOrderLifecycle:
    def __init__(self) -> None:
        self.deleted_future: list[tuple[RecurringOrderId, date]] = []
        self.deleted_for_rebuild: list[tuple[RecurringOrderId, date]] = []

    async def delete_future_orders(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
        self.deleted_future.append((recurring_order_id, from_date))

    async def delete_future_orders_for_rebuild(
        self,
        recurring_order_id: RecurringOrderId,
        from_date: date,
        current_user: CurrentUserDTO,
    ) -> None:
        self.deleted_for_rebuild.append((recurring_order_id, from_date))


class FakeRecurringOrderExecution:
    def __init__(self) -> None:
        self.requests: list[RecurringOrderExecutionRequest] = []

    async def run(
        self, request: RecurringOrderExecutionRequest
    ) -> RecurringOrderExecutionResult:
        self.requests.append(request)
        return RecurringOrderExecutionResult(
            created_dates=[],
            already_scheduled_dates=[],
            cancelled_dates=[],
            paused=False,
        )


class FakeSchedulingClock:
    def future_order_cutoff(self) -> date:
        return FUTURE_CUTOFF


class FakeTemplateIntegrity:
    def __init__(self, runnable: bool = True) -> None:
        self.runnable = runnable

    async def is_runnable(self, recurring_order: RecurringOrder) -> bool:
        return self.runnable


class FakeTransactionManager:
    def __init__(self) -> None:
        self.flushed = False

    async def flush(self) -> None:
        self.flushed = True


def _current_user() -> CurrentUserDTO:
    return CurrentUserDTO(
        user_id=UserId(UUID("55555555-5555-5555-5555-555555555555")),
        full_name="Manager",
        role=ShopRole.MANAGER,
        shop_id=SHOP_ID,
    )


def _recurring_order(
    *, status: RecurringOrderStatus = RecurringOrderStatus.ACTIVE
) -> RecurringOrder:
    return RecurringOrder(
        id=RECURRING_ORDER_ID,
        shop_id=SHOP_ID,
        client_id=CLIENT_ID,
        address_id=None,
        phone_id=None,
        time_slot_id=TIME_SLOT_ID,
        payment_method="Готівка",
        comment=None,
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        status=status,
    )


def _lifecycle(
    *,
    gateway: FakeRecurringOrderGateway | None = None,
    generated: FakeGeneratedOrderLifecycle | None = None,
    execution: FakeRecurringOrderExecution | None = None,
    integrity: FakeTemplateIntegrity | None = None,
    tr_manager: FakeTransactionManager | None = None,
) -> RecurringOrderLifecycle:
    return RecurringOrderLifecycle(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            gateway or FakeRecurringOrderGateway(),
        ),
        cast(
            "GeneratedOrderLifecycle",
            generated or FakeGeneratedOrderLifecycle(),
        ),
        cast(
            "RecurringOrderExecution",
            execution or FakeRecurringOrderExecution(),
        ),
        cast("RecurringOrderSchedulingClock", FakeSchedulingClock()),
        cast(
            "RecurringOrderTemplateIntegrity",
            integrity or FakeTemplateIntegrity(),
        ),
        cast("TransactionManager", tr_manager or FakeTransactionManager()),
    )


@pytest.mark.asyncio()
async def test_pause_can_delete_future_orders() -> None:
    generated = FakeGeneratedOrderLifecycle()
    recurring_order = _recurring_order()
    lifecycle = _lifecycle(generated=generated)

    await lifecycle.pause(
        recurring_order,
        _current_user(),
        cancel_future_orders=True,
    )

    assert recurring_order.status == RecurringOrderStatus.PAUSED
    assert generated.deleted_future == [(RECURRING_ORDER_ID, FUTURE_CUTOFF)]


@pytest.mark.asyncio()
async def test_resume_requires_runnable_template() -> None:
    recurring_order = _recurring_order(status=RecurringOrderStatus.PAUSED)
    lifecycle = _lifecycle(integrity=FakeTemplateIntegrity(runnable=False))

    with pytest.raises(RecurringOrderTemplateInvalidError):
        await lifecycle.resume(recurring_order)

    assert recurring_order.status == RecurringOrderStatus.PAUSED


@pytest.mark.asyncio()
async def test_resume_activates_runnable_template() -> None:
    recurring_order = _recurring_order(status=RecurringOrderStatus.PAUSED)
    lifecycle = _lifecycle(integrity=FakeTemplateIntegrity(runnable=True))

    await lifecycle.resume(recurring_order)

    assert recurring_order.status == RecurringOrderStatus.ACTIVE


@pytest.mark.asyncio()
async def test_delete_optionally_deletes_future_orders_then_template() -> None:
    gateway = FakeRecurringOrderGateway()
    generated = FakeGeneratedOrderLifecycle()
    recurring_order = _recurring_order()
    lifecycle = _lifecycle(gateway=gateway, generated=generated)

    await lifecycle.delete(
        recurring_order,
        _current_user(),
        delete_future_orders=True,
    )

    assert generated.deleted_future == [(RECURRING_ORDER_ID, FUTURE_CUTOFF)]
    assert gateway.deleted == [recurring_order]


@pytest.mark.asyncio()
async def test_rebuild_future_orders_rejects_paused_template() -> None:
    generated = FakeGeneratedOrderLifecycle()
    execution = FakeRecurringOrderExecution()
    tr_manager = FakeTransactionManager()
    recurring_order = _recurring_order(status=RecurringOrderStatus.PAUSED)
    lifecycle = _lifecycle(
        generated=generated,
        execution=execution,
        tr_manager=tr_manager,
    )

    with pytest.raises(RecurringOrderPausedError):
        await lifecycle.rebuild_future_orders(recurring_order, _current_user())

    assert generated.deleted_for_rebuild == []
    assert tr_manager.flushed is False
    assert execution.requests == []


@pytest.mark.asyncio()
async def test_rebuild_future_orders_deletes_flushes_and_generates() -> None:
    generated = FakeGeneratedOrderLifecycle()
    execution = FakeRecurringOrderExecution()
    tr_manager = FakeTransactionManager()
    recurring_order = _recurring_order(status=RecurringOrderStatus.ACTIVE)
    lifecycle = _lifecycle(
        generated=generated,
        execution=execution,
        tr_manager=tr_manager,
    )

    await lifecycle.rebuild_future_orders(recurring_order, _current_user())

    assert generated.deleted_for_rebuild == [
        (RECURRING_ORDER_ID, FUTURE_CUTOFF)
    ]
    assert tr_manager.flushed is True
    assert execution.requests == [
        RecurringOrderExecutionRequest(
            recurring_order_id=RECURRING_ORDER_ID,
            shop_id=SHOP_ID,
            include_today=False,
        )
    ]
