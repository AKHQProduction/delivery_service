import uuid
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderFilters,
)
from backend.application.dto.idp import CurrentUserDTO
from backend.application.services.recurring_order_planning_read import (
    RecurringOrderPlanningRead,
)
from backend.application.vars import (
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    ShopRole,
    UserId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderReadGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)


def _current_user(shop_id: ShopId) -> CurrentUserDTO:
    return CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        full_name="Manager",
        role=ShopRole.MANAGER,
        shop_id=shop_id,
    )


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


async def _time_slot_id(
    session: AsyncSession, shop_id: uuid.UUID
) -> uuid.UUID:
    result = await session.execute(
        select(ShopDeliveryTimeSlot.id).where(
            ShopDeliveryTimeSlot.shop_id == shop_id
        )
    )
    time_slot_id = result.scalars().first()
    assert time_slot_id is not None
    return time_slot_id


@pytest.mark.asyncio()
async def test_recurring_order_planning_read_lists_and_details_current_shop(
    session: AsyncSession,
    setup_full_test_user_with_shop: Any,
    create_shop: Any,
    setup_test_client: Any,
    setup_test_product: Any,
    setup_test_time_slot: Any,
) -> None:
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=9300)
    other_shop_id = await create_shop()
    client_id = await setup_test_client(
        shop_id=shop_id,
        full_name="Олена Коваль",
        phones=["+380501111111"],
        addresses=[{"street": "Хрещатик", "house": "10"}],
    )
    other_client_id = await setup_test_client(
        shop_id=other_shop_id,
        full_name="Олена Інший магазин",
        phones=["+380502222222"],
        addresses=[{"street": "Саксаганського", "house": "20"}],
    )
    product_id, product_name, product_price, _ = await setup_test_product(
        shop_id=shop_id
    )
    other_product_id, _, _, _ = await setup_test_product(shop_id=other_shop_id)
    phone_id, address_id = await _client_refs(session, client_id)
    other_phone_id, other_address_id = await _client_refs(
        session, other_client_id
    )
    time_slot_id = await _time_slot_id(session, shop_id)
    other_time_slot_id = await setup_test_time_slot(shop_id=other_shop_id)

    recurring_order_id = uuid.uuid4()
    session.add(
        RecurringOrder(
            id=recurring_order_id,
            shop_id=shop_id,
            client_id=client_id,
            address_id=address_id,
            phone_id=phone_id,
            time_slot_id=time_slot_id,
            payment_method="Готівка",
            comment="Передзвонити",
            schedule_type=ScheduleType.MONTHLY_BY_DAY,
            weekdays=None,
            month_days=[5, 20],
            status=RecurringOrderStatus.ACTIVE,
        )
    )
    session.add(
        RecurringOrderItem(
            recurring_order_id=recurring_order_id,
            product_id=product_id,
            quantity=2,
        )
    )
    other_recurring_order_id = uuid.uuid4()
    session.add(
        RecurringOrder(
            id=other_recurring_order_id,
            shop_id=other_shop_id,
            client_id=other_client_id,
            address_id=other_address_id,
            phone_id=other_phone_id,
            time_slot_id=other_time_slot_id,
            payment_method="Готівка",
            schedule_type=ScheduleType.MONTHLY_BY_DAY,
            weekdays=None,
            month_days=[5],
            status=RecurringOrderStatus.ACTIVE,
        )
    )
    session.add(
        RecurringOrderItem(
            recurring_order_id=other_recurring_order_id,
            product_id=other_product_id,
            quantity=1,
        )
    )
    await session.flush()

    planning_read = RecurringOrderPlanningRead(
        SQLAlchemyRecurringOrderReadGateway(session)
    )

    rows = await planning_read.list(
        _current_user(shop_id),
        RecurringOrderFilters(
            client_id=client_id,
            client_name="Олена",
            month_day=5,
        ),
    )

    assert len(rows) == 1
    row = rows[0]
    assert row.recurring_order_id == recurring_order_id
    assert row.client_name == "Олена Коваль"
    assert row.address_summary == "Хрещатик, 10"
    assert row.month_days == [5, 20]
    assert row.items_count == 1

    detail = await planning_read.detail(
        _current_user(shop_id), RecurringOrderId(recurring_order_id)
    )

    assert detail.payment_method == "Готівка"
    assert detail.comment == "Передзвонити"
    assert [
        (item.product_name, item.quantity, item.current_price)
        for item in detail.items
    ] == [
        (product_name, 2, int(Decimal(product_price))),
    ]
