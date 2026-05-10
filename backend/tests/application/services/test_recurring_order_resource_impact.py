from typing import cast
from uuid import UUID

import pytest

from backend.application.dto.idp import CurrentUserDTO
from backend.application.services.recurring_order_resource_impact import (
    RecurringOrderResourceImpact,
)
from backend.application.vars import (
    ClientId,
    ProductId,
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
    RecurringOrderItem,
)

SHOP_ID = ShopId(UUID("11111111-1111-1111-1111-111111111111"))
OTHER_SHOP_ID = ShopId(UUID("99999999-9999-9999-9999-999999999999"))
PRODUCT_ID = ProductId(UUID("22222222-2222-2222-2222-222222222222"))
OTHER_PRODUCT_ID = ProductId(UUID("33333333-3333-3333-3333-333333333333"))
TIME_SLOT_ID = TimeSlotId(UUID("44444444-4444-4444-4444-444444444444"))
CLIENT_ID = ClientId(UUID("55555555-5555-5555-5555-555555555555"))


class FakeRecurringOrderGateway:
    def __init__(self, recurring_orders: list[RecurringOrder]) -> None:
        self.recurring_orders = recurring_orders

    async def load_by_product(
        self, product_id: ProductId
    ) -> list[RecurringOrder]:
        return [
            recurring_order
            for recurring_order in self.recurring_orders
            if any(
                item.product_id == product_id for item in recurring_order.items
            )
        ]

    async def load_by_time_slot(
        self, time_slot_id: TimeSlotId
    ) -> list[RecurringOrder]:
        return [
            recurring_order
            for recurring_order in self.recurring_orders
            if recurring_order.time_slot_id == time_slot_id
        ]


def _current_user() -> CurrentUserDTO:
    return CurrentUserDTO(
        user_id=UserId(UUID("66666666-6666-6666-6666-666666666666")),
        full_name="Manager",
        role=ShopRole.MANAGER,
        shop_id=SHOP_ID,
    )


def _recurring_order(
    recurring_order_id: str,
    *,
    shop_id: ShopId = SHOP_ID,
    product_id: ProductId = PRODUCT_ID,
    time_slot_id: TimeSlotId = TIME_SLOT_ID,
) -> RecurringOrder:
    recurring_order = RecurringOrder(
        id=RecurringOrderId(UUID(recurring_order_id)),
        shop_id=shop_id,
        client_id=CLIENT_ID,
        address_id=None,
        phone_id=None,
        time_slot_id=time_slot_id,
        payment_method="Готівка",
        comment=None,
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        status=RecurringOrderStatus.ACTIVE,
    )
    recurring_order.items = [
        RecurringOrderItem(
            recurring_order_id=recurring_order.id,
            product_id=product_id,
            quantity=1,
        )
    ]
    return recurring_order


@pytest.mark.asyncio()
async def test_deleted_product_pauses_affected_recurring_orders_only() -> None:
    affected = _recurring_order(
        "77777777-7777-7777-7777-777777777777",
        product_id=PRODUCT_ID,
    )
    unrelated = _recurring_order(
        "88888888-8888-8888-8888-888888888888",
        product_id=OTHER_PRODUCT_ID,
    )
    impact = RecurringOrderResourceImpact(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            FakeRecurringOrderGateway([affected, unrelated]),
        )
    )

    await impact.pause_for_deleted_product(PRODUCT_ID, _current_user())

    assert affected.status == RecurringOrderStatus.PAUSED
    assert unrelated.status == RecurringOrderStatus.ACTIVE


@pytest.mark.asyncio()
async def test_deleted_time_slot_pauses_affected_recurring_orders_only() -> (
    None
):
    other_time_slot_id = TimeSlotId(
        UUID("99999999-9999-9999-9999-999999999999")
    )
    affected = _recurring_order(
        "77777777-7777-7777-7777-777777777777",
        time_slot_id=TIME_SLOT_ID,
    )
    unrelated = _recurring_order(
        "88888888-8888-8888-8888-888888888888",
        time_slot_id=other_time_slot_id,
    )
    impact = RecurringOrderResourceImpact(
        cast(
            "SQLAlchemyRecurringOrderGateway",
            FakeRecurringOrderGateway([affected, unrelated]),
        )
    )

    await impact.pause_for_deleted_time_slot(TIME_SLOT_ID, _current_user())

    assert affected.status == RecurringOrderStatus.PAUSED
    assert affected.time_slot_id is None
    assert unrelated.status == RecurringOrderStatus.ACTIVE
    assert unrelated.time_slot_id == other_time_slot_id
