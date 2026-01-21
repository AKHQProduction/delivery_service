import uuid
from datetime import UTC, datetime, timedelta

import pytest

from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderItemDTO,
)
from backend.application.queries.get_orders import (
    GetOrdersQuery,
    GetOrdersQueryHandler,
)
from backend.application.vars import (
    ClientId,
    OrderId,
    PaymentMethod,
    ShopId,
    ShopRole,
    TimePreference,
    UserId,
)
from backend.infrastructure.in_memory import (
    InMemoryIdentityProvider,
    InMemoryOrderGateway,
)


@pytest.fixture()
def make_handler():
    def _make_handler(
        user_id: UserId | None = None,
        shop_id: ShopId | None = None,
        role: ShopRole = ShopRole.OWNER,
    ):
        if not user_id:
            user_id = UserId(uuid.uuid4())
        if not shop_id:
            shop_id = ShopId(uuid.uuid4())
        idp = InMemoryIdentityProvider(
            user_id=user_id, role=role, shop_id=shop_id
        )
        order_gateway = InMemoryOrderGateway()

        handler = GetOrdersQueryHandler(idp=idp, order_gateway=order_gateway)

        return handler, idp, order_gateway, shop_id

    return _make_handler


def create_order_dto(
    order_id: OrderId,
    shop_id: ShopId,
    client_id: ClientId | None = None,
    delivery_date: datetime | None = None,
    time_preference: TimePreference = TimePreference.FIRST_HALF,
) -> CreateOrderDTO:
    return CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id or ClientId(uuid.uuid4()),
        delivery_date=delivery_date
        or (datetime.now(UTC).date() + timedelta(days=1)),
        time_preference=time_preference,
        delivery_phone="+380501234567",
        delivery_address=DeliveryAddressDTO(
            street="Test Street",
            house="1",
        ),
        order_items=[
            OrderItemDTO(name="Test Product", quantity=1, price_per_item=100)
        ],
        comment=None,
        payment_method=PaymentMethod.CASH,
    )


@pytest.mark.asyncio()
async def test_get_orders_returns_list(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    for _ in range(3):
        order_id = OrderId(uuid.uuid4())
        await order_gateway.create_order(
            create_order_dto(order_id, shop_id, client_id)
        )

    query = GetOrdersQuery(pagination=Pagination(limit=100, offset=0))
    result = await handler.handle(query)

    assert len(result) == 3


@pytest.mark.asyncio()
async def test_get_orders_filters_by_shop_id(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    other_shop_id = ShopId(uuid.uuid4())
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    for _ in range(2):
        order_id = OrderId(uuid.uuid4())
        await order_gateway.create_order(
            create_order_dto(order_id, shop_id, client_id)
        )

    for _ in range(3):
        order_id = OrderId(uuid.uuid4())
        await order_gateway.create_order(
            create_order_dto(order_id, other_shop_id, client_id)
        )

    query = GetOrdersQuery(pagination=Pagination(limit=100, offset=0))
    result = await handler.handle(query)

    assert len(result) == 2


@pytest.mark.asyncio()
async def test_get_orders_filters_by_date(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    today = datetime.now(UTC).date()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()), shop_id, client_id, delivery_date=tomorrow
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()), shop_id, client_id, delivery_date=tomorrow
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()), shop_id, client_id, delivery_date=day_after
        )
    )

    query = GetOrdersQuery(
        pagination=Pagination(limit=100, offset=0),
        start_date=tomorrow,
        end_date=tomorrow,
    )
    result = await handler.handle(query)

    assert len(result) == 2
    assert all(order.date == tomorrow for order in result)


@pytest.mark.asyncio()
async def test_get_orders_filters_by_time_preference(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            time_preference=TimePreference.FIRST_HALF,
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            time_preference=TimePreference.FIRST_HALF,
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            time_preference=TimePreference.SECOND_HALF,
        )
    )

    query = GetOrdersQuery(
        pagination=Pagination(limit=100, offset=0),
        time_preference=TimePreference.FIRST_HALF,
    )
    result = await handler.handle(query)

    assert len(result) == 2
    assert all(
        order.time_preference == TimePreference.FIRST_HALF for order in result
    )


@pytest.mark.asyncio()
async def test_get_orders_with_pagination(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    for i in range(5):
        order_id = OrderId(uuid.uuid4())
        await order_gateway.create_order(
            create_order_dto(
                order_id,
                shop_id,
                client_id,
                delivery_date=datetime.now(UTC).date() + timedelta(days=i + 1),
            )
        )

    query_page1 = GetOrdersQuery(pagination=Pagination(limit=2, offset=0))
    result_page1 = await handler.handle(query_page1)

    query_page2 = GetOrdersQuery(pagination=Pagination(limit=2, offset=2))
    result_page2 = await handler.handle(query_page2)

    query_page3 = GetOrdersQuery(pagination=Pagination(limit=2, offset=4))
    result_page3 = await handler.handle(query_page3)

    assert len(result_page1) == 2
    assert len(result_page2) == 2
    assert len(result_page3) == 1

    all_order_ids = [
        o.order_id for o in result_page1 + result_page2 + result_page3
    ]
    assert len(all_order_ids) == len(set(all_order_ids))


@pytest.mark.asyncio()
async def test_get_orders_sorted_by_date(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    today = datetime.now(UTC).date()

    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=today + timedelta(days=3),
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=today + timedelta(days=1),
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=today + timedelta(days=2),
        )
    )

    query = GetOrdersQuery(pagination=Pagination(limit=100, offset=0))
    result = await handler.handle(query)

    assert len(result) == 3
    assert result[0].date == today + timedelta(days=1)
    assert result[1].date == today + timedelta(days=2)
    assert result[2].date == today + timedelta(days=3)


@pytest.mark.asyncio()
async def test_get_orders_empty_list(make_handler) -> None:
    handler, _, _, _ = make_handler()

    query = GetOrdersQuery(pagination=Pagination(limit=100, offset=0))
    result = await handler.handle(query)

    assert result == []


@pytest.mark.asyncio()
async def test_get_orders_with_combined_filters(make_handler) -> None:
    handler, _, order_gateway, shop_id = make_handler()
    client_id = ClientId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    tomorrow = datetime.now(UTC).date() + timedelta(days=1)

    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=tomorrow,
            time_preference=TimePreference.FIRST_HALF,
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=tomorrow,
            time_preference=TimePreference.SECOND_HALF,
        )
    )
    await order_gateway.create_order(
        create_order_dto(
            OrderId(uuid.uuid4()),
            shop_id,
            client_id,
            delivery_date=datetime.now(UTC).date() + timedelta(days=2),
            time_preference=TimePreference.FIRST_HALF,
        )
    )

    query = GetOrdersQuery(
        pagination=Pagination(limit=100, offset=0),
        start_date=tomorrow,
        end_date=tomorrow,
        time_preference=TimePreference.FIRST_HALF,
    )
    result = await handler.handle(query)

    assert len(result) == 1
    assert result[0].date == tomorrow
    assert result[0].time_preference == TimePreference.FIRST_HALF
