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


def map_order_to_read_model(
    order: Order,
    customer: CustomerReadModel,
    address: AddressReadModel | None = None,
) -> OrderReadModel:
    return OrderReadModel(
        order_id=order.id,
        customer=customer,
        delivery_date=order.date,
        delivery_preference=order.delivery_time_preference,
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
    )
