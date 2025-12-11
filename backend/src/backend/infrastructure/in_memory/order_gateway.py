import uuid

from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    OrderGateway,
)
from backend.application.vars import OrderId


class InMemoryOrderGateway(OrderGateway):
    def __init__(self, order_id: OrderId | None = None) -> None:
        self.orders: dict[OrderId, CreateOrderDTO] = {}
        self.order_id = order_id

    def next_id(self) -> OrderId:
        return self.order_id or OrderId(uuid.uuid4())

    async def create_order(self, dto: CreateOrderDTO) -> None:
        self.orders[dto.order_id] = dto
