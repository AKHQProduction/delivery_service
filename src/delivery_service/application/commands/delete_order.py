import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    OrderNotFoundError,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.orders.repository import OrderRepository
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shops.repository import ShopRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteOrderRequest(TelegramRequest[None]):
    order_id: OrderID


class DeleteOrderHandler(RequestHandler[DeleteOrderRequest, None]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_repository: ShopRepository,
        order_repository: OrderRepository,
    ) -> None:
        self._idp = idp
        self._shop_repository = shop_repository
        self._order_repository = order_repository

    async def handle(self, request: DeleteOrderRequest) -> None:
        logger.info("Request to delete order %s", request.order_id)
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise AccessDeniedError()
        order = await self._order_repository.load_with_id(request.order_id)
        if not order:
            raise OrderNotFoundError()

        shop.can_delete_order(
            order_shop_id=order.shop_reference, deleter_id=current_user_id
        )
        await self._order_repository.delete(order)
        logger.info("Order %s successfully deleted", request.order_id)
