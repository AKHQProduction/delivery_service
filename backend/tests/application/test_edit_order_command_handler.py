import uuid
from datetime import UTC, datetime, timedelta

import pytest

from backend.application.commands.edit_order import (
    OrderItem,
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
)
from backend.application.errors import (
    AccessDeniedError,
    DateMustBeGreaterThanError,
    EntityNotFoundError,
)
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    ClientDM,
    PhoneDTO,
)
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderItemDTO,
)
from backend.application.interfaces.gateways.product_gateway import Product
from backend.application.vars import (
    AddressId,
    AddressType,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PhoneId,
    ProductCategory,
    ProductId,
    ShopId,
    ShopRole,
    TimePreference,
    UserId,
)
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryClientGateway,
    InMemoryIdentityProvider,
    InMemoryOrderGateway,
)
from backend.infrastructure.in_memory.product_gateway import (
    InMemoryProductGateway,
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
        client_gateway = InMemoryClientGateway()
        product_gateway = InMemoryProductGateway()
        order_gateway = InMemoryOrderGateway()
        tr_manager = FakeTransactionManager()

        handler = UpdateOrderCommandHandler(
            idp=idp,
            client_gateway=client_gateway,
            product_gateway=product_gateway,
            order_gateway=order_gateway,
            tr_manager=tr_manager,
        )

        return (
            handler,
            idp,
            client_gateway,
            product_gateway,
            order_gateway,
            tr_manager,
        )

    return _make_handler


def create_order_dto(
    order_id: OrderId,
    shop_id: ShopId,
    client_id: ClientId | None = None,
    comment: str | None = "Initial comment",
    product_id: ProductId | None = None,
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
            address_type=AddressType.APARTMENT,
        ),
        order_items=[
            OrderItemDTO(
                id=1,
                name="Test Product",
                quantity=1,
                price_per_item=100,
                product_id=product_id,
            )
        ],
        comment=comment,
    )


def create_client(
    client_id: ClientId,
    shop_id: ShopId,
) -> ClientDM:
    return ClientDM(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Test Client",
        phones=[
            PhoneDTO(id=PhoneId(1), number="+380501234567", is_primary=True),
            PhoneDTO(id=PhoneId(2), number="+380509876543", is_primary=False),
        ],
        addresses=[
            AddressDTO(
                id=AddressId(1),
                street="Street 1",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                is_primary=True,
            ),
            AddressDTO(
                id=AddressId(2),
                street="Street 2",
                house="20",
                address_type=AddressType.PRIVATE_HOUSE,
                is_primary=False,
            ),
        ],
    )


@pytest.mark.asyncio()
async def test_update_order_delivery_date(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    new_date = datetime.now(UTC).date() + timedelta(days=5)
    command = UpdateOrderCommand(
        order_id=order_id,
        delivery_date=new_date,
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.delivery_date == new_date
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_time_preference(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        time_preference=TimePreference.SECOND_HALF,
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.time_preference == TimePreference.SECOND_HALF
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_comment(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        comment="New comment",
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.comment == "New comment"
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_clear_order_comment(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, comment="Some comment")
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        comment=Empty.EMPTY,
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.comment is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_change_client(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    original_client_id = ClientId(uuid.uuid4())
    new_client_id = ClientId(uuid.uuid4())

    # Create clients
    client_gateway.clients[original_client_id] = create_client(
        original_client_id, shop_id
    )
    new_client = create_client(new_client_id, shop_id)
    new_client = ClientDM(
        client_id=new_client_id,
        shop_id=shop_id,
        full_name="New Client",
        phones=[
            PhoneDTO(id=PhoneId(1), number="+380111111111", is_primary=True),
        ],
        addresses=[
            AddressDTO(
                id=AddressId(1),
                street="New Street",
                house="100",
                address_type=AddressType.APARTMENT,
                apartment="50",
                is_primary=True,
            ),
        ],
    )
    client_gateway.clients[new_client_id] = new_client

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=original_client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        client_id=new_client_id,
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.client_id == new_client_id
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_change_phone(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    client_id = ClientId(uuid.uuid4())
    client_gateway.clients[client_id] = create_client(client_id, shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        phone_id=PhoneId(2),
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.delivery_phone == "+380509876543"
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_change_address(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    client_id = ClientId(uuid.uuid4())
    client_gateway.clients[client_id] = create_client(client_id, shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        address_id=AddressId(2),
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.delivery_address.street == "Street 2"
    assert updated_order.delivery_address.house == "20"
    assert (
        updated_order.delivery_address.address_type
        == AddressType.PRIVATE_HOUSE
    )
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_replace_items(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, product_gateway, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    product_id = ProductId(uuid.uuid4())
    product_gateway.products[product_id] = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="New Product",
        price=200,
        category=ProductCategory.WATER,
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        items=[OrderItem(product_id=product_id, quantity=3)],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert len(updated_order.order_items) == 1
    new_item = updated_order.order_items[0]
    assert new_item.name == "New Product"
    assert new_item.quantity == 3
    assert new_item.price_per_item == 200
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_keep_existing_item_and_add_new(
    make_handler,
) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, product_gateway, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    new_product_id = ProductId(uuid.uuid4())
    product_gateway.products[new_product_id] = Product(
        product_id=new_product_id,
        shop_id=shop_id,
        name="New Product",
        price=200,
        category=ProductCategory.WATER,
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    # Keep existing item (id + quantity), add new item (product_id required)
    command = UpdateOrderCommand(
        order_id=order_id,
        items=[
            OrderItem(quantity=5, id=OrderItemId(1)),
            OrderItem(product_id=new_product_id, quantity=3),
        ],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert len(updated_order.order_items) == 2

    existing_item = updated_order.order_items[0]
    assert existing_item.id == OrderItemId(1)
    assert existing_item.quantity == 5

    new_item = updated_order.order_items[1]
    assert new_item.name == "New Product"
    assert new_item.quantity == 3
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_remove_items_by_not_including(
    make_handler,
) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    order_dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=ClientId(uuid.uuid4()),
        delivery_date=datetime.now(UTC).date() + timedelta(days=1),
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=DeliveryAddressDTO(
            street="Test Street",
            house="1",
            address_type=AddressType.APARTMENT,
        ),
        order_items=[
            OrderItemDTO(
                quantity=1, name="Product 1", price_per_item=100, id=1
            ),
            OrderItemDTO(
                quantity=2, name="Product 2", price_per_item=200, id=2
            ),
            OrderItemDTO(
                quantity=3, name="Product 3", price_per_item=300, id=3
            ),
        ],
        comment=None,
    )
    await order_gateway.create_order(order_dto)

    command = UpdateOrderCommand(
        order_id=order_id,
        items=[
            OrderItem(quantity=5, id=OrderItemId(1)),
        ],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert len(updated_order.order_items) == 1
    assert updated_order.order_items[0].id == OrderItemId(1)
    assert updated_order.order_items[0].quantity == 5
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_access_denied_courier(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id, role=ShopRole.COURIER
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        comment="New comment",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_access_denied_different_shop(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, other_shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        comment="New comment",
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_not_found(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, _, tr_manager = make_handler(shop_id=shop_id)

    non_existent_order_id = OrderId(uuid.uuid4())
    command = UpdateOrderCommand(
        order_id=non_existent_order_id,
        comment="New comment",
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Order"
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_client_not_found(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    non_existent_client_id = ClientId(uuid.uuid4())
    command = UpdateOrderCommand(
        order_id=order_id,
        client_id=non_existent_client_id,
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Client"
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_phone_not_found(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    client_id = ClientId(uuid.uuid4())
    client_gateway.clients[client_id] = create_client(client_id, shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        phone_id=PhoneId(999),
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Phone"
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_address_not_found(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    client_id = ClientId(uuid.uuid4())
    client_gateway.clients[client_id] = create_client(client_id, shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        address_id=AddressId(999),
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Address"
    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_product_not_found(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    non_existent_product_id = ProductId(uuid.uuid4())
    command = UpdateOrderCommand(
        order_id=order_id,
        items=[OrderItem(product_id=non_existent_product_id, quantity=1)],
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Product"
    assert not tr_manager.committed


def test_update_order_date_in_past_raises_error() -> None:
    yesterday = datetime.now(UTC).date() - timedelta(days=1)

    with pytest.raises(DateMustBeGreaterThanError):
        UpdateOrderCommand(
            order_id=OrderId(uuid.uuid4()),
            delivery_date=yesterday,
        )


@pytest.mark.parametrize("role", (ShopRole.OWNER, ShopRole.MANAGER))
@pytest.mark.asyncio()
async def test_owner_and_manager_can_update_order(
    role: ShopRole, make_handler
) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id, role=role
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(create_order_dto(order_id, shop_id))

    command = UpdateOrderCommand(
        order_id=order_id,
        comment="Updated by " + role.value,
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.comment == f"Updated by {role.value}"
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_new_client_from_different_shop_denied(
    make_handler,
) -> None:
    shop_id = ShopId(uuid.uuid4())
    other_shop_id = ShopId(uuid.uuid4())
    handler, _, client_gateway, _, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    # Original client in user's shop
    original_client_id = ClientId(uuid.uuid4())
    client_gateway.clients[original_client_id] = create_client(
        original_client_id, shop_id
    )

    # New client in different shop
    new_client_id = ClientId(uuid.uuid4())
    client_gateway.clients[new_client_id] = create_client(
        new_client_id, other_shop_id
    )

    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, client_id=original_client_id)
    )

    command = UpdateOrderCommand(
        order_id=order_id,
        client_id=new_client_id,
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)

    assert not tr_manager.committed


@pytest.mark.asyncio()
async def test_update_order_no_changes(make_handler) -> None:
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    order_id = OrderId(uuid.uuid4())
    original_dto = create_order_dto(order_id, shop_id)
    await order_gateway.create_order(original_dto)

    command = UpdateOrderCommand(order_id=order_id)

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    assert updated_order.delivery_date == original_dto.delivery_date
    assert updated_order.time_preference == original_dto.time_preference
    assert updated_order.comment == original_dto.comment
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_item_quantity_auto_fetches_current_price(
    make_handler,
) -> None:
    """Item with product_id in DB auto-fetches current price on update."""
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, product_gateway, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    # Create product with initial price
    product_id = ProductId(uuid.uuid4())
    product_gateway.products[product_id] = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )

    # Create order with product_id linked
    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, product_id=product_id)
    )

    # Change product price
    product_gateway.products[product_id] = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=150,  # New price
        category=ProductCategory.WATER,
    )

    # Update only quantity, no product_id passed
    command = UpdateOrderCommand(
        order_id=order_id,
        items=[OrderItem(quantity=5, id=OrderItemId(1))],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    item = updated_order.order_items[0]
    assert item.quantity == 5
    assert item.price_per_item == 150  # Auto-updated to current price
    assert item.product_id == product_id
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_old_item_without_product_id_keeps_old_price(
    make_handler,
) -> None:
    """Old items without product_id keep their existing price."""
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, _, order_gateway, tr_manager = make_handler(shop_id=shop_id)

    # Create order without product_id (legacy order)
    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, product_id=None)
    )

    # Update only quantity
    command = UpdateOrderCommand(
        order_id=order_id,
        items=[OrderItem(quantity=10, id=OrderItemId(1))],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    item = updated_order.order_items[0]
    assert item.quantity == 10
    assert item.price_per_item == 100  # Kept old price
    assert item.product_id is None
    assert tr_manager.committed


@pytest.mark.asyncio()
async def test_update_item_with_explicit_product_id(make_handler) -> None:
    """When product_id is explicitly passed, use that product's price."""
    shop_id = ShopId(uuid.uuid4())
    handler, _, _, product_gateway, order_gateway, tr_manager = make_handler(
        shop_id=shop_id
    )

    # Create original product
    original_product_id = ProductId(uuid.uuid4())
    product_gateway.products[original_product_id] = Product(
        product_id=original_product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )

    # Create new product
    new_product_id = ProductId(uuid.uuid4())
    product_gateway.products[new_product_id] = Product(
        product_id=new_product_id,
        shop_id=shop_id,
        name="Вода 12л",
        price=80,
        category=ProductCategory.WATER,
    )

    # Create order with original product
    order_id = OrderId(uuid.uuid4())
    await order_gateway.create_order(
        create_order_dto(order_id, shop_id, product_id=original_product_id)
    )

    # Update with new product_id
    command = UpdateOrderCommand(
        order_id=order_id,
        items=[
            OrderItem(quantity=2, id=OrderItemId(1), product_id=new_product_id)
        ],
    )

    await handler.handle(command)

    updated_order = order_gateway.orders[order_id]
    item = updated_order.order_items[0]
    assert item.quantity == 2
    assert item.name == "Вода 12л"
    assert item.price_per_item == 80
    assert item.product_id == new_product_id
    assert tr_manager.committed
