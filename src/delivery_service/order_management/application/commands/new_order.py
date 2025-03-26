from dataclasses import dataclass

from bazario import Request
from bazario.asyncio import RequestHandler

from delivery_service.identity.public.identity_id import UserID
from delivery_service.order_management.domain.factory import OrderLineData
from delivery_service.shared.application.ports.shop_provider import (
    ShopProvider,
)


@dataclass(frozen=True)
class NewOrderRequest(Request[None]):
    order_lines: list[OrderLineData]
    customer_id: UserID


class NewOrderHandler(RequestHandler[NewOrderRequest, None]):
    def __init__(self, shop_provider: ShopProvider) -> None:
        self._shop_provider = shop_provider

    async def handle(self, request: NewOrderRequest) -> None:
        await self._shop_provider.get_current_shop_id()
