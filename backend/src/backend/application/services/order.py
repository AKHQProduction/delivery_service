from datetime import date, time
from decimal import Decimal

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.gateways.order_gateway import OrderItemDTO
from backend.application.errors import EntityNotFoundError
from backend.application.vars import (
    AddressId,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PaymentMethod,
    PhoneId,
    ProductId,
    ShopId,
)
from backend.infrastructure.persistence.tables.base import DeliveryAddressDTO
from backend.infrastructure.persistence.tables.clients import (
    Client,
)
from backend.infrastructure.persistence.tables.orders import (
    Order,
    OrderItem,
)
from backend.infrastructure.persistence.tables.products import Product


def resolve_phone(client: Client, phone_id: PhoneId) -> str:
    phone = next((p for p in client.phones if p.id == phone_id), None)
    if not phone:
        raise EntityNotFoundError(entity="Phone")
    return phone.number


def resolve_address(
    client: Client, address_id: AddressId
) -> DeliveryAddressDTO:
    address = next((a for a in client.addresses if a.id == address_id), None)
    if not address:
        raise EntityNotFoundError(entity="Address")
    return DeliveryAddressDTO(
        street=address.street,
        house=address.house,
        apartment=address.apartment,
        entrance=address.entrance,
        floor=address.floor,
        intercom=address.intercom,
        comment=address.comment,
        district=address.district.name if address.district else None,
        coordinates=CoordinatesDTO.build(address.latitude, address.longitude),
    )


def resolve_order_items(
    items: list[tuple[OrderItemId | None, int, ProductId | None]],
    existing_items: list[OrderItem],
    products: list[Product],
) -> list[OrderItemDTO]:
    existing_map = {item.id: item for item in existing_items}
    products_map: dict[ProductId, tuple[str, Decimal]] = {
        p.id: (p.name, p.price) for p in products
    }

    result: list[OrderItemDTO] = []
    for item_id, quantity, explicit_product_id in items:
        product_id = explicit_product_id
        if product_id is None and item_id is not None:
            existing = existing_map.get(item_id)
            if existing and existing.product_id:
                product_id = existing.product_id

        name: str | None = None
        price: Decimal | None = None
        if product_id is not None and product_id in products_map:
            name, price = products_map[product_id]

        result.append(
            OrderItemDTO(
                quantity=quantity,
                name=name,
                price_per_item=price,
                id=item_id,
                product_id=product_id,
            )
        )
    return result


def create_order(
    *,
    order_id: OrderId,
    shop_id: ShopId,
    client_id: ClientId,
    delivery_date: date,
    delivery_start_time: time,
    delivery_end_time: time,
    delivery_phone: str,
    delivery_address: DeliveryAddressDTO,
    payment_method: PaymentMethod,
    comment: str | None,
) -> Order:
    return Order(
        id=order_id,
        date=delivery_date,
        delivery_address=delivery_address,
        delivery_phone=delivery_phone,
        delivery_start_time=delivery_start_time,
        delivery_end_time=delivery_end_time,
        comment=comment,
        shop_id=shop_id,
        client_id=client_id,
        payment_method=payment_method,
    )


def update_order(
    order: Order,
    *,
    client_id: ClientId | None = None,
    delivery_date: date | None = None,
    delivery_start_time: time | None = None,
    delivery_end_time: time | None = None,
    delivery_phone: str | None = None,
    delivery_address: DeliveryAddressDTO | None = None,
    comment: str | Empty | None = None,
    payment_method: PaymentMethod | None = None,
) -> None:
    if client_id is not None:
        order.client_id = client_id
    if delivery_date is not None:
        order.date = delivery_date
    if delivery_start_time is not None:
        order.delivery_start_time = delivery_start_time
    if delivery_end_time is not None:
        order.delivery_end_time = delivery_end_time
    if delivery_phone is not None:
        order.delivery_phone = delivery_phone
    if delivery_address is not None:
        order.delivery_address = delivery_address
    if comment is not None:
        order.comment = None if comment == Empty.EMPTY else comment
    if payment_method is not None:
        order.payment_method = payment_method.value


def update_order_items(
    order: Order,
    item_dtos: list[OrderItemDTO],
) -> list[OrderItem]:
    existing_items_map = {item.id: item for item in order.items}
    new_ids = {dto.id for dto in item_dtos if dto.id is not None}

    removed = [item for item in order.items if item.id not in new_ids]

    for dto in item_dtos:
        if dto.id is not None and dto.id in existing_items_map:
            item = existing_items_map[dto.id]
            item.quantity = dto.quantity
            if dto.name is not None:
                item.name = dto.name
            if dto.price_per_item is not None:
                item.price_per_item = dto.price_per_item
            if dto.product_id is not None:
                item.product_id = dto.product_id
        else:
            order.items.append(
                OrderItem(
                    name=dto.name or "",
                    quantity=dto.quantity,
                    price_per_item=dto.price_per_item or 0,
                    order_id=order.id,
                    product_id=dto.product_id,
                )
            )

    return removed


def create_order_item(
    *,
    name: str,
    quantity: int,
    price_per_item: Decimal,
    product_id: ProductId | None = None,
) -> OrderItem:
    return OrderItem(
        name=name,
        quantity=quantity,
        price_per_item=price_per_item,
        product_id=product_id,
    )
