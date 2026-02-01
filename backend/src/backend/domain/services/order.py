from datetime import date, time
from decimal import Decimal

from backend.application.vars import (
    ClientId,
    OrderId,
    PaymentMethod,
    ProductId,
    ShopId,
)
from backend.infrastructure.persistence.tables.orders import (
    Order,
    OrderItem,
)


def create_order(
    *,
    order_id: OrderId,
    shop_id: ShopId,
    client_id: ClientId,
    delivery_date: date,
    delivery_start_time: time,
    delivery_end_time: time,
    delivery_phone: str,
    delivery_address: dict,
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
