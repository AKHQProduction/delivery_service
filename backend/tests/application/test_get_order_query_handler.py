import uuid
from datetime import UTC, date, datetime, timedelta

import pytest

from backend.application.errors import EntityNotFoundError
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderItemDTO,
)
from backend.application.queries.get_order import GetOrderQueryHandler
from backend.application.vars import (
    AddressType,
    ClientId,
    OrderId,
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

        handler = GetOrderQueryHandler(idp=idp, order_gateway=order_gateway)

        return handler, idp, order_gateway

    return _make_handler


def create_order_dto(
    order_id: OrderId,
    shop_id: ShopId,
    client_id: ClientId | None = None,
    delivery_date: date | None = None,
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
            address_type=AddressType.APARTMENT,
        ),
        order_items=[
            OrderItemDTO(name="Test Product", quantity=1, price_per_item=100)
        ],
        comment="Test comment",
    )


@pytest.mark.asyncio()
async def test_get_order_success(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    client_id = ClientId(uuid.uuid4())
    handler, _, order_gateway = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    order_id = OrderId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id)
    )

    result = await handler.handle(order_id=order_id)

    assert result.order_id == order_id
    assert result.client_id == client_id
    assert result.client_name == "Test Client"
    assert result.delivery_phone == "+380501234567"
    assert result.delivery_address.street == "Test Street"
    assert result.comment == "Test comment"
    assert len(result.items) == 1
    assert result.items[0].name == "Test Product"


@pytest.mark.asyncio()
async def test_get_order_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_order_id = OrderId(uuid.uuid4())

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(order_id=non_existent_order_id)

    assert "Order" in exc_info.value.message


@pytest.mark.asyncio()
async def test_get_order_from_different_shop_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())
    handler, _, order_gateway = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, other_shop_id))

    with pytest.raises(EntityNotFoundError):
        await handler.handle(order_id=order_id)


@pytest.mark.asyncio()
async def test_get_order_with_multiple_items(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    client_id = ClientId(uuid.uuid4())
    handler, _, order_gateway = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    order_id = OrderId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=datetime.now(UTC).date() + timedelta(days=1),
        time_preference=TimePreference.SECOND_HALF,
        delivery_phone="+380501234567",
        delivery_address=DeliveryAddressDTO(
            street="Test Street",
            house="1",
            address_type=AddressType.APARTMENT,
        ),
        order_items=[
            OrderItemDTO(name="Product 1", quantity=2, price_per_item=100),
            OrderItemDTO(name="Product 2", quantity=1, price_per_item=200),
            OrderItemDTO(name="Product 3", quantity=5, price_per_item=50),
        ],
        comment=None,
    )
    await order_gateway.create_order(dto)

    result = await handler.handle(order_id=order_id)

    assert len(result.items) == 3
    assert result.items[0].name == "Product 1"
    assert result.items[0].quantity == 2
    assert result.items[1].name == "Product 2"
    assert result.items[2].name == "Product 3"
    assert result.time_preference == TimePreference.SECOND_HALF
    assert result.comment is None


@pytest.mark.asyncio()
async def test_get_order_by_courier(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    client_id = ClientId(uuid.uuid4())
    handler, _, order_gateway = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    order_id = OrderId(uuid.uuid4())
    order_gateway.client_names[client_id] = "Test Client"
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id)
    )

    result = await handler.handle(order_id=order_id)

    assert result.order_id == order_id
