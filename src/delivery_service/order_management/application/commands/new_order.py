from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.identity.public.identity_id import UserID
from delivery_service.order_management.domain.factory import OrderLineData


@dataclass(frozen=True)
class NewOrderRequest(Request[None]):
    order_lines: list[OrderLineData]
    customer_id: UserID


class NewOrderHandler(RequestHandler[NewOrderRequest, None]):
    def __init__(self) -> None:
        pass

    async def handle(self, request: NewOrderRequest) -> None:
        pass
