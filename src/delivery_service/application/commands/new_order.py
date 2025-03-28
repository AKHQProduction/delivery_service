from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.domain.orders.factory import OrderLineData
from delivery_service.domain.shared.user_id import UserID


@dataclass(frozen=True)
class NewOrderRequest(Request[None]):
    order_lines: list[OrderLineData]
    customer_id: UserID


class NewOrderHandler(RequestHandler[NewOrderRequest, None]):
    def __init__(self) -> None:
        pass

    async def handle(self, request: NewOrderRequest) -> None:
        pass
