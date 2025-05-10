from datetime import time

from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerReadModel,
)
from delivery_service.application.query.ports.order_gateway import (
    OrderLineReadModel,
    OrderReadModel,
)
from delivery_service.domain.orders.order import Order

TIME_SLOTS_TO_TEXT = {
    time(hour=9): "З 9 до 12",
    time(hour=12): "З 12 до 15",
    time(hour=15): "З 15 до 18",
    time(hour=18): "З 18 до 21",
}


def map_order_to_read_model(
    order: Order,
    customer: CustomerReadModel,
    address: AddressReadModel | None = None,
) -> OrderReadModel:
    return OrderReadModel(
        order_id=order.id,
        customer=customer,
        delivery_date=order.date,
        time_slot=TIME_SLOTS_TO_TEXT[
            order.delivery_time_preference.start_time
        ],
        order_lines=[
            OrderLineReadModel(
                order_line_id=line.id,
                title=line.line_title,
                price_per_item=line.unit_price.value,
                quantity=line.total_quantity.value,
            )
            for line in order.order_lines
        ],
        total_order_price=order.total_order_price.value,
        address=address,
        phone_number=order.phone_number,
        note=order.note if order.note else "Відсутня",
    )
