from decimal import Decimal

from backend.application.errors import (
    InvalidOrderTotalError,
    OrderAlreadyPaidError,
)
from backend.application.services.payment_method import (
    BALANCE_PAYMENT_METHOD_NAME,
)
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.orders import Order


def calculate_order_total(order: Order) -> Decimal:
    total = sum(
        (item.price_per_item * item.quantity for item in order.items),
        start=Decimal(0),
    )
    if total <= 0:
        raise InvalidOrderTotalError
    return total


def apply_balance_payment(
    order: Order,
    client: Client,
    *,
    total: Decimal | None = None,
) -> Decimal:
    if order.is_paid:
        raise OrderAlreadyPaidError

    total = total if total is not None else calculate_order_total(order)
    client.balance -= total
    order.payment_method = BALANCE_PAYMENT_METHOD_NAME
    order.is_paid = True
    return total


def revert_balance_payment(
    order: Order,
    client: Client,
    *,
    total: Decimal | None = None,
) -> Decimal:
    total = total if total is not None else calculate_order_total(order)
    client.balance += total
    order.is_paid = False
    return total


def sync_balance_payment_amount(
    *,
    order: Order,
    client: Client,
    previous_total: Decimal,
) -> Decimal:
    new_total = calculate_order_total(order)
    delta = new_total - previous_total
    client.balance -= delta
    order.payment_method = BALANCE_PAYMENT_METHOD_NAME
    order.is_paid = True
    return delta
