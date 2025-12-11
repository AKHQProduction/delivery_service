import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderItemDTO,
)
from backend.application.vars import (
    AddressType,
    OrderId,
    TimePreference,
)
from backend.infrastructure.persistence.gateways import SQLAlchemyOrderGateway
from backend.infrastructure.persistence.tables.orders import Order, OrderItem


def test_next_id_returns_uuid_v7(
    order_gateway: SQLAlchemyOrderGateway,
) -> None:
    result = order_gateway.next_id()

    assert isinstance(result, uuid.UUID)
    assert result.version == 7


def test_next_id_returns_unique_ids(
    order_gateway: SQLAlchemyOrderGateway,
) -> None:
    id1 = order_gateway.next_id()
    id2 = order_gateway.next_id()
    id3 = order_gateway.next_id()

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3
    assert all(isinstance(order_id, uuid.UUID) for order_id in [id1, id2, id3])


@pytest.mark.asyncio()
async def test_create_order_saves_basic_data(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
        entrance="1",
        floor="2",
        intercom="123",
    )

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=[],
        comment="Доставити до 12:00",
    )

    await order_gateway.create_order(dto)
    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()

    assert order.id == order_id
    assert order.shop_id == shop_id
    assert order.client_id == client_id
    assert order.date == delivery_date
    assert order.time_preference == TimePreference.FIRST_HALF.value
    assert order.delivery_phone == "+380501234567"
    assert order.comment == "Доставити до 12:00"


@pytest.mark.asyncio()
async def test_create_order_saves_delivery_address_as_json(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Шевченка",
        house="20",
        address_type=AddressType.PRIVATE_HOUSE,
        apartment=None,
        entrance=None,
        floor=None,
        intercom=None,
    )

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.SECOND_HALF,
        delivery_phone="+380507654321",
        delivery_address=delivery_address,
        order_items=[],
        comment=None,
    )

    await order_gateway.create_order(dto)
    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()

    assert order.delivery_address["street"] == "Шевченка"
    assert order.delivery_address["house"] == "20"
    assert (
        order.delivery_address["address_type"]
        == AddressType.PRIVATE_HOUSE.value
    )
    assert order.delivery_address["apartment"] is None
    assert order.delivery_address["entrance"] is None
    assert order.delivery_address["floor"] is None
    assert order.delivery_address["intercom"] is None


@pytest.mark.asyncio()
async def test_create_order_with_single_order_item(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
    )

    order_item = OrderItemDTO(
        name="Вода 19л",
        quantity=2,
        price_per_item=100,
    )

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=[order_item],
        comment=None,
    )

    await order_gateway.create_order(dto)
    await session.flush()

    result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = result.scalars().all()

    assert len(items) == 1
    assert items[0].name == "Вода 19л"
    assert items[0].quantity == 2
    assert items[0].price_per_item == 100


@pytest.mark.asyncio()
async def test_create_order_with_multiple_order_items(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
    )

    order_items = [
        OrderItemDTO(name="Вода 19л", quantity=3, price_per_item=100),
        OrderItemDTO(name="Помпа", quantity=1, price_per_item=50),
        OrderItemDTO(name="Стаканчики", quantity=50, price_per_item=2),
    ]

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.SECOND_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=order_items,
        comment="Доставити після 14:00",
    )

    await order_gateway.create_order(dto)
    await session.flush()

    result = await session.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.id)
    )
    items = result.scalars().all()

    assert len(items) == 3
    assert items[0].name == "Вода 19л"
    assert items[0].quantity == 3
    assert items[0].price_per_item == 100
    assert items[1].name == "Помпа"
    assert items[1].quantity == 1
    assert items[1].price_per_item == 50
    assert items[2].name == "Стаканчики"
    assert items[2].quantity == 50
    assert items[2].price_per_item == 2


@pytest.mark.asyncio()
async def test_create_order_without_comment(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
    )

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=[],
        comment=None,
    )

    await order_gateway.create_order(dto)
    await session.flush()

    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()

    assert order.comment is None


@pytest.mark.asyncio()
async def test_create_order_with_different_time_preferences(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
    )

    # Test FIRST_HALF
    order_id_1 = OrderId(uuid.uuid4())
    dto_1 = CreateOrderDTO(
        order_id=order_id_1,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=[],
        comment=None,
    )
    await order_gateway.create_order(dto_1)

    # Test SECOND_HALF
    order_id_2 = OrderId(uuid.uuid4())
    dto_2 = CreateOrderDTO(
        order_id=order_id_2,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.SECOND_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=[],
        comment=None,
    )
    await order_gateway.create_order(dto_2)

    await session.flush()

    result_1 = await session.execute(
        select(Order).where(Order.id == order_id_1)
    )
    order_1 = result_1.scalar_one()
    assert order_1.time_preference == TimePreference.FIRST_HALF.value

    result_2 = await session.execute(
        select(Order).where(Order.id == order_id_2)
    )
    order_2 = result_2.scalar_one()
    assert order_2.time_preference == TimePreference.SECOND_HALF.value


@pytest.mark.asyncio()
async def test_order_items_linked_to_order_via_relationship(
    session: AsyncSession,
    order_gateway: SQLAlchemyOrderGateway,
    create_shop,
    setup_test_client,
) -> None:
    shop_id = await create_shop()
    client_id = await setup_test_client(shop_id)
    order_id = OrderId(uuid.uuid4())
    delivery_date = datetime.now(UTC).date() + timedelta(days=1)

    delivery_address = DeliveryAddressDTO(
        street="Хрещатик",
        house="10",
        address_type=AddressType.APARTMENT,
        apartment="5",
    )

    order_items = [
        OrderItemDTO(name="Вода 19л", quantity=2, price_per_item=100),
    ]

    dto = CreateOrderDTO(
        order_id=order_id,
        shop_id=shop_id,
        client_id=client_id,
        delivery_date=delivery_date,
        time_preference=TimePreference.FIRST_HALF,
        delivery_phone="+380501234567",
        delivery_address=delivery_address,
        order_items=order_items,
        comment=None,
    )

    await order_gateway.create_order(dto)
    await session.flush()

    # Verify items are accessible through order relationship
    result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = result.scalars().all()

    assert len(items) == 1
    assert items[0].order_id == order_id
