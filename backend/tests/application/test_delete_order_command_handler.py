import uuid
from datetime import UTC, datetime, timedelta

import pytest

from backend.application.commands.delete_order import (
    DeleteOrderCommand,
    DeleteOrderCommandHandler,
)
from backend.application.errors import AccessDeniedError
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderItemDTO,
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
    FakeTransactionManager,
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
        tr_manager = FakeTransactionManager()

        handler = DeleteOrderCommandHandler(
            idp=idp, order_gateway=order_gateway, tr_manager=tr_manager
        )

        return handler, idp, order_gateway, tr_manager

    return _make_handler


def create_order_dto(
    order_id: OrderId, shop_id: ShopId, client_id: ClientId | None = None
) -> CreateOrderDTO:
    return CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id or ClientId(uuid.uuid4()),
        delivery_date=datetime.now(UTC).date() + timedelta(days=1),
        time_preference=TimePreference.FIRST_HALF,
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
async def test_delete_order_success(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, order_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = DeleteOrderCommand(order_id=order_id)

    await handler.handle(command)

    deleted_order = await order_gateway.load(order_id)
    assert deleted_order is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_order_success_by_manager(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, order_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.MANAGER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = DeleteOrderCommand(order_id=order_id)

    await handler.handle(command)

    deleted_order = await order_gateway.load(order_id)
    assert deleted_order is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_order_access_denied_courier(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, order_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = DeleteOrderCommand(order_id=order_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    order = await order_gateway.load(order_id)
    assert order is not None
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_order_not_found(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    non_existent_order_id = OrderId(uuid.uuid4())
    command = DeleteOrderCommand(order_id=non_existent_order_id)

    await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_delete_order_access_denied_different_shop(make_handler) -> None:
    user_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())

    handler, _, order_gateway, tr_manager = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, other_shop_id))

    command = DeleteOrderCommand(order_id=order_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    order = await order_gateway.load(order_id)
    assert order is not None
    assert not tr_manager.committed
