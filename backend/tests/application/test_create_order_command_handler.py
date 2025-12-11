import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from backend.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
    ProductDTO,
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
from backend.application.interfaces.gateways.product_gateway import Product
from backend.application.vars import (
    AddressId,
    AddressType,
    ClientId,
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

        handler = CreateOrderCommandHandler(
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


@pytest.fixture()
def client_id():
    return ClientId(uuid.uuid4())


@pytest.fixture()
def address_id():
    return AddressId(1)


@pytest.fixture()
def phone_id():
    return PhoneId(1)


@pytest.fixture()
def product_id():
    return ProductId(uuid.uuid4())


@pytest_asyncio.fixture()
async def setup_client_and_product(
    make_handler, client_id, address_id, phone_id, product_id
):
    shop_id = ShopId(uuid.uuid4())
    user_id = UserId(uuid.uuid4())
    handler, _, client_gateway, product_gateway, order_gateway, tr_manager = (
        make_handler(user_id=user_id, shop_id=shop_id)
    )

    # Create client
    client = ClientDM(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(id=phone_id, number="+380501234567", is_primary=True)
        ],
        addresses=[
            AddressDTO(
                id=address_id,
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                is_primary=True,
            )
        ],
    )
    client_gateway.clients[client_id] = client

    # Create product
    product = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )
    product_gateway.products[product_id] = product

    return (
        handler,
        shop_id,
        user_id,
        client_gateway,
        product_gateway,
        order_gateway,
        tr_manager,
    )


@pytest.mark.asyncio()
async def test_create_order_successfully(
    setup_client_and_product,
    client_id,
    address_id,
    phone_id,
    product_id,
) -> None:
    handler, shop_id, _, _, _, order_gateway, tr_manager = (
        setup_client_and_product
    )
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=2)],
        comment="Доставити до 12:00",
    )

    order_id = await handler.handle(command)

    assert len(order_gateway.orders) == 1
    assert order_id in order_gateway.orders
    assert tr_manager.committed is True

    created_order = order_gateway.orders[order_id]
    assert created_order.shop_id == shop_id
    assert created_order.client_id == client_id
    assert created_order.delivery_date == delivery_date
    assert created_order.time_preference == TimePreference.FIRST_HALF
    assert created_order.delivery_phone == "+380501234567"
    assert created_order.delivery_address.street == "Хрещатик"
    assert created_order.delivery_address.house == "10"
    assert created_order.delivery_address.apartment == "5"
    assert len(created_order.order_items) == 1
    assert created_order.order_items[0].name == "Вода 19л"
    assert created_order.order_items[0].quantity == 2
    assert created_order.order_items[0].price_per_item == 100
    assert created_order.comment == "Доставити до 12:00"


@pytest.mark.asyncio()
async def test_create_order_with_multiple_products(
    setup_client_and_product,
    client_id,
    address_id,
    phone_id,
) -> None:
    handler, shop_id, _, _, product_gateway, order_gateway, _ = (
        setup_client_and_product
    )

    # Add second product
    product_id_2 = ProductId(uuid.uuid4())
    product_2 = Product(
        product_id=product_id_2,
        shop_id=shop_id,
        name="Помпа",
        price=50,
        category=ProductCategory.OTHER,
    )
    product_gateway.products[product_id_2] = product_2

    delivery_date = datetime.now(UTC).date() + timedelta(days=1)
    product_id_1 = next(iter(product_gateway.products.keys()))

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.SECOND_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[
            ProductDTO(product_id=product_id_1, quantity=3),
            ProductDTO(product_id=product_id_2, quantity=1),
        ],
    )

    order_id = await handler.handle(command)

    created_order = order_gateway.orders[order_id]
    assert len(created_order.order_items) == 2
    assert created_order.order_items[0].name == "Вода 19л"
    assert created_order.order_items[0].quantity == 3
    assert created_order.order_items[1].name == "Помпа"
    assert created_order.order_items[1].quantity == 1


@pytest.mark.asyncio()
async def test_create_order_without_comment(
    setup_client_and_product,
    client_id,
    address_id,
    phone_id,
    product_id,
) -> None:
    handler, _, _, _, _, order_gateway, _ = setup_client_and_product
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    order_id = await handler.handle(command)

    created_order = order_gateway.orders[order_id]
    assert created_order.comment is None


@pytest.mark.asyncio()
async def test_raise_error_when_client_not_found(
    make_handler, address_id, phone_id, product_id
) -> None:
    handler, _, _, _, _, _ = make_handler()
    non_existent_client_id = ClientId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=non_existent_client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Client"


@pytest.mark.asyncio()
async def test_raise_error_when_phone_not_found(
    setup_client_and_product, client_id, address_id, product_id
) -> None:
    handler, *_ = setup_client_and_product
    non_existent_phone_id = PhoneId(999)
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=non_existent_phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Phone"


@pytest.mark.asyncio()
async def test_raise_error_when_address_not_found(
    setup_client_and_product, client_id, phone_id, product_id
) -> None:
    handler, *_ = setup_client_and_product
    non_existent_address_id = AddressId(999)
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=non_existent_address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Address"


@pytest.mark.asyncio()
async def test_raise_error_when_product_not_found(
    setup_client_and_product, client_id, address_id, phone_id
) -> None:
    handler, *_ = setup_client_and_product
    non_existent_product_id = ProductId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=non_existent_product_id, quantity=1)],
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert exc_info.value._entity == "Product"


@pytest.mark.asyncio()
async def test_raise_error_when_user_is_courier(
    make_handler, client_id, address_id, phone_id, product_id
) -> None:
    shop_id = ShopId(uuid.uuid4())
    user_id = UserId(uuid.uuid4())
    handler, _, client_gateway, product_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id, role=ShopRole.COURIER
    )

    # Setup client and product for courier
    client = ClientDM(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(id=phone_id, number="+380501234567", is_primary=True)
        ],
        addresses=[
            AddressDTO(
                id=address_id,
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                is_primary=True,
            )
        ],
    )
    client_gateway.clients[client_id] = client

    product = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )
    product_gateway.products[product_id] = product

    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_error_when_client_belongs_to_different_shop(
    make_handler, client_id, address_id, phone_id, product_id
) -> None:
    shop_id_1 = ShopId(uuid.uuid4())
    shop_id_2 = ShopId(uuid.uuid4())
    user_id = UserId(uuid.uuid4())

    handler, _, client_gateway, product_gateway, _, _ = make_handler(
        user_id=user_id, shop_id=shop_id_1
    )

    # Create client for different shop
    client = ClientDM(
        client_id=client_id,
        shop_id=shop_id_2,  # Different shop!
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(id=phone_id, number="+380501234567", is_primary=True)
        ],
        addresses=[
            AddressDTO(
                id=address_id,
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                is_primary=True,
            )
        ],
    )
    client_gateway.clients[client_id] = client

    product = Product(
        product_id=product_id,
        shop_id=shop_id_1,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )
    product_gateway.products[product_id] = product

    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_error_when_delivery_date_is_in_past() -> None:
    yesterday = datetime.now(UTC).date() - timedelta(days=1)

    with pytest.raises(DateMustBeGreaterThanError):
        CreateOrderCommand(
            client_id=ClientId(uuid.uuid4()),
            delivery_date=yesterday,
            time_preference=TimePreference.FIRST_HALF,
            address_id=AddressId(1),
            phone_id=PhoneId(1),
            products=[
                ProductDTO(product_id=ProductId(uuid.uuid4()), quantity=1)
            ],
        )


@pytest.mark.parametrize("role", (ShopRole.OWNER, ShopRole.MANAGER))
@pytest.mark.asyncio()
async def test_owner_and_manager_can_create_order(
    client_id,
    address_id,
    phone_id,
    product_id,
    role: ShopRole,
    make_handler,
) -> None:
    shop_id = ShopId(uuid.uuid4())
    user_id = UserId(uuid.uuid4())
    handler, _, client_gateway, product_gateway, order_gateway, _ = (
        make_handler(user_id=user_id, shop_id=shop_id, role=role)
    )

    # Setup client and product
    client = ClientDM(
        client_id=client_id,
        shop_id=shop_id,
        full_name="Іван Іванов",
        phones=[
            PhoneDTO(id=phone_id, number="+380501234567", is_primary=True)
        ],
        addresses=[
            AddressDTO(
                id=address_id,
                street="Хрещатик",
                house="10",
                address_type=AddressType.APARTMENT,
                apartment="5",
                is_primary=True,
            )
        ],
    )
    client_gateway.clients[client_id] = client

    product = Product(
        product_id=product_id,
        shop_id=shop_id,
        name="Вода 19л",
        price=100,
        category=ProductCategory.WATER,
    )
    product_gateway.products[product_id] = product

    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.SECOND_HALF,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    order_id = await handler.handle(command)

    assert order_id in order_gateway.orders


@pytest.mark.parametrize(
    "time_pref", (TimePreference.FIRST_HALF, TimePreference.SECOND_HALF)
)
@pytest.mark.asyncio()
async def test_create_order_with_different_time_preferences(
    setup_client_and_product,
    client_id,
    address_id,
    phone_id,
    product_id,
    time_pref: TimePreference,
) -> None:
    handler, _, _, _, _, order_gateway, _ = setup_client_and_product
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    command = CreateOrderCommand(
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=time_pref,
        address_id=address_id,
        phone_id=phone_id,
        products=[ProductDTO(product_id=product_id, quantity=1)],
    )

    order_id = await handler.handle(command)

    created_order = order_gateway.orders[order_id]
    assert created_order.time_preference == time_pref
