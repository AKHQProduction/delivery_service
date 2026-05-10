from typing import cast
from uuid import UUID

import pytest

from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.services.recurring_order_management_context import (
    RecurringOrderManagementContext,
)
from backend.application.vars import (
    ClientId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    ShopRole,
    UserId,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)

SHOP_ID = ShopId(UUID("11111111-1111-1111-1111-111111111111"))
OTHER_SHOP_ID = ShopId(UUID("99999999-9999-9999-9999-999999999999"))
USER_ID = UserId(UUID("22222222-2222-2222-2222-222222222222"))
CLIENT_ID = ClientId(UUID("33333333-3333-3333-3333-333333333333"))
RECURRING_ORDER_ID = RecurringOrderId(
    UUID("44444444-4444-4444-4444-444444444444")
)


class FakeIdentityProvider:
    def __init__(self, current_user: CurrentUserDTO) -> None:
        self._current_user = current_user

    async def current_user(self) -> CurrentUserDTO:
        return self._current_user


class FakeRecurringOrderGateway:
    def __init__(self, recurring_order: RecurringOrder | None) -> None:
        self.recurring_order = recurring_order
        self.loaded_with_items = False

    async def load(
        self, recurring_order_id: RecurringOrderId
    ) -> RecurringOrder | None:
        if (
            self.recurring_order
            and self.recurring_order.id == recurring_order_id
        ):
            return self.recurring_order
        return None

    async def load_with_items(
        self, recurring_order_id: RecurringOrderId
    ) -> RecurringOrder | None:
        self.loaded_with_items = True
        return await self.load(recurring_order_id)


def _current_user(*, role: ShopRole = ShopRole.MANAGER) -> CurrentUserDTO:
    return CurrentUserDTO(
        user_id=USER_ID,
        full_name="Manager",
        role=role,
        shop_id=SHOP_ID,
    )


def _recurring_order(*, shop_id: ShopId = SHOP_ID) -> RecurringOrder:
    return RecurringOrder(
        id=RECURRING_ORDER_ID,
        shop_id=shop_id,
        client_id=CLIENT_ID,
        address_id=None,
        phone_id=None,
        time_slot_id=None,
        payment_method="Готівка",
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        status=RecurringOrderStatus.ACTIVE,
    )


def _context(
    current_user: CurrentUserDTO,
    gateway: FakeRecurringOrderGateway,
) -> RecurringOrderManagementContext:
    return RecurringOrderManagementContext(
        cast("IdentityProvider", FakeIdentityProvider(current_user)),
        cast("SQLAlchemyRecurringOrderGateway", gateway),
    )


@pytest.mark.asyncio()
async def test_current_manager_returns_manager() -> None:
    current_user = _current_user()
    context = _context(current_user, FakeRecurringOrderGateway(None))

    assert await context.current_manager() == current_user


@pytest.mark.asyncio()
async def test_current_manager_rejects_courier() -> None:
    context = _context(
        _current_user(role=ShopRole.COURIER),
        FakeRecurringOrderGateway(None),
    )

    with pytest.raises(AccessDeniedError):
        await context.current_manager()


@pytest.mark.asyncio()
async def test_load_owned_returns_same_shop_recurring_order() -> None:
    recurring_order = _recurring_order()
    context = _context(
        _current_user(),
        FakeRecurringOrderGateway(recurring_order),
    )

    assert (
        await context.load_owned(RECURRING_ORDER_ID, _current_user())
        == recurring_order
    )


@pytest.mark.asyncio()
async def test_load_owned_rejects_other_shop_recurring_order() -> None:
    context = _context(
        _current_user(),
        FakeRecurringOrderGateway(_recurring_order(shop_id=OTHER_SHOP_ID)),
    )

    with pytest.raises(AccessDeniedError):
        await context.load_owned(RECURRING_ORDER_ID, _current_user())


@pytest.mark.asyncio()
async def test_load_owned_with_items_uses_items_loader() -> None:
    gateway = FakeRecurringOrderGateway(_recurring_order())
    context = _context(_current_user(), gateway)

    await context.load_owned_with_items(RECURRING_ORDER_ID, _current_user())

    assert gateway.loaded_with_items is True


@pytest.mark.asyncio()
async def test_load_owned_raises_not_found() -> None:
    context = _context(_current_user(), FakeRecurringOrderGateway(None))

    with pytest.raises(EntityNotFoundError):
        await context.load_owned(RECURRING_ORDER_ID, _current_user())
