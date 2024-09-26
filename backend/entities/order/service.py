from decimal import Decimal

from entities.order.models import OrderItem


def total_price(order_items: list[OrderItem]) -> Decimal:
    return Decimal(sum(item.amount.total_price() for item in order_items))
