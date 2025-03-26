from delivery_service.order_management.domain.order_line import OrderLine


class OrderLineCollection(set[OrderLine]):
    def add_line(self, order_line: OrderLine) -> None:
        pass
