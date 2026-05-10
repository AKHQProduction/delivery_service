from datetime import time
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest

from backend.application.services.recurring_order_template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    PhoneId,
    ProductId,
    RecurringOrderId,
    RecurringOrderStatus,
    ScheduleType,
    ShopId,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
    ClientPhone,
)
from backend.infrastructure.persistence.tables.products import Product
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
    RecurringOrderItem,
)
from backend.infrastructure.persistence.tables.shops import (
    ShopDeliveryTimeSlot,
)

SHOP_ID = ShopId(UUID("11111111-1111-1111-1111-111111111111"))
OTHER_SHOP_ID = ShopId(UUID("99999999-9999-9999-9999-999999999999"))
CLIENT_ID = ClientId(UUID("22222222-2222-2222-2222-222222222222"))
PRODUCT_ID = ProductId(UUID("33333333-3333-3333-3333-333333333333"))
TIME_SLOT_ID = TimeSlotId(UUID("44444444-4444-4444-4444-444444444444"))
ADDRESS_ID = AddressId(10)
PHONE_ID = PhoneId(20)


class FakeClientGateway:
    def __init__(self, client: Client | None) -> None:
        self.client = client

    async def load(self, client_id: ClientId) -> Client | None:
        if self.client and self.client.id == client_id:
            return self.client
        return None


class FakeProductGateway:
    def __init__(self, products: list[Product]) -> None:
        self.products = products

    async def load_many(self, product_ids: list[ProductId]) -> list[Product]:
        return [
            product for product in self.products if product.id in product_ids
        ]


class FakeTimeSlotGateway:
    def __init__(self, time_slot: ShopDeliveryTimeSlot | None) -> None:
        self.time_slot = time_slot

    async def load(
        self, time_slot_id: TimeSlotId
    ) -> ShopDeliveryTimeSlot | None:
        if self.time_slot and self.time_slot.id == time_slot_id:
            return self.time_slot
        return None


def _client(*, shop_id: ShopId = SHOP_ID) -> Client:
    client = Client(id=CLIENT_ID, shop_id=shop_id, full_name="Client")
    client.addresses = [
        ClientAddress(
            id=ADDRESS_ID,
            client_id=CLIENT_ID,
            street="Хрещатик",
            house="10",
        )
    ]
    client.phones = [
        ClientPhone(
            id=PHONE_ID,
            client_id=CLIENT_ID,
            shop_id=shop_id,
            number="+380501111111",
            is_primary=True,
        )
    ]
    return client


def _product(*, shop_id: ShopId = SHOP_ID) -> Product:
    return Product(
        id=PRODUCT_ID,
        shop_id=shop_id,
        name="Water",
        price=Decimal(100),
    )


def _time_slot(*, shop_id: ShopId = SHOP_ID) -> ShopDeliveryTimeSlot:
    return ShopDeliveryTimeSlot(
        id=TIME_SLOT_ID,
        shop_id=shop_id,
        start_time=time(9),
        end_time=time(12),
    )


def _recurring_order() -> RecurringOrder:
    recurring_order = RecurringOrder(
        id=RecurringOrderId(UUID("55555555-5555-5555-5555-555555555555")),
        shop_id=SHOP_ID,
        client_id=CLIENT_ID,
        address_id=ADDRESS_ID,
        phone_id=PHONE_ID,
        time_slot_id=TIME_SLOT_ID,
        payment_method="Готівка",
        schedule_type=ScheduleType.WEEKLY,
        weekdays=[1],
        month_days=None,
        status=RecurringOrderStatus.ACTIVE,
    )
    recurring_order.items = [
        RecurringOrderItem(
            recurring_order_id=recurring_order.id,
            product_id=PRODUCT_ID,
            quantity=1,
        )
    ]
    return recurring_order


def _integrity(
    *,
    client: Client | None = None,
    products: list[Product] | None = None,
    time_slot: ShopDeliveryTimeSlot | None = None,
) -> RecurringOrderTemplateIntegrity:
    return RecurringOrderTemplateIntegrity(
        cast(
            "SQLAlchemyClientGateway", FakeClientGateway(client or _client())
        ),
        cast(
            "SQLAlchemyProductGateway",
            FakeProductGateway([_product()] if products is None else products),
        ),
        cast(
            "SQLAlchemyTimeSlotGateway",
            FakeTimeSlotGateway(time_slot or _time_slot()),
        ),
    )


@pytest.mark.asyncio()
async def test_runnable_template_returns_true() -> None:
    assert await _integrity().is_runnable(_recurring_order()) is True


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "field",
    ("address_id", "phone_id", "time_slot_id"),
)
async def test_missing_required_reference_returns_false(field: str) -> None:
    recurring_order = _recurring_order()
    setattr(recurring_order, field, None)

    assert await _integrity().is_runnable(recurring_order) is False


@pytest.mark.asyncio()
async def test_missing_product_returns_false() -> None:
    assert (
        await _integrity(products=[]).is_runnable(_recurring_order()) is False
    )


@pytest.mark.asyncio()
async def test_cross_shop_resource_returns_false() -> None:
    assert (
        await _integrity(
            products=[_product(shop_id=OTHER_SHOP_ID)]
        ).is_runnable(_recurring_order())
        is False
    )
