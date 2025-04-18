import logging
from dataclasses import dataclass
from datetime import date

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.orders.order import DeliveryPreference
from delivery_service.domain.orders.order_id import OrderID
from delivery_service.domain.shared.dto import OrderLineData
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.repository import ShopRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MakeNewOrderRequest(TelegramRequest[OrderID]):
    customer_id: UserID
    order_lines: list[OrderLineData]
    delivery_preference: DeliveryPreference
    bottles_to_exchange: int
    delivery_date: date


class MakeNewOrderHandler(RequestHandler[MakeNewOrderRequest, OrderID]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_repository: ShopRepository,
        id_generator: IDGenerator,
    ) -> None:
        self._idp = idp
        self._shop_repository = shop_repository
        self._id_generator = id_generator

    async def handle(self, request: MakeNewOrderRequest) -> OrderID:
        logger.info("Request to make new order")
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise AccessDeniedError()

        new_order_id = self._id_generator.generate_order_id()
        new_order = shop.add_new_order(
            new_order_id=new_order_id,
            customer_id=request.customer_id,
            order_line_data=request.order_lines,
            delivery_date=request.delivery_date,
            delivery_preference=request.delivery_preference,
            bottles_to_exchange=request.bottles_to_exchange,
            creator_id=current_user_id,
        )

        logger.info("Successfully create new order %s", new_order.id)
        return new_order.id
