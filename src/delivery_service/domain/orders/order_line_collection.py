from delivery_service.domain.orders.order_line import OrderLine


class OrderLineCollection(set[OrderLine]):
    def add_line(self, order_line: OrderLine) -> None:
        pass
