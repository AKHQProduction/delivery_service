import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.order.errors import (
    OrderItemNotFoundError,
)
from application.order.gateway import OrderItemReader, OrderReader
from application.shop.shop_validate import ShopValidationService
from application.user.errors import UserNotFoundError
from entities.order.models import OrderItemId
from entities.order.service import total_price
from entities.order.value_objects import OrderTotalPrice
from entities.shop.models import ShopId


@dataclass(frozen=True)
class EditOrderItemQuantityInputData:
    order_item_id: int
    quantity: int
    shop_id: int | None = None


class EditOrderItemQuantity(Interactor[EditOrderItemQuantityInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        shop_validation: ShopValidationService,
        order_item_reader: OrderItemReader,
        order_reader: OrderReader,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._shop_validation = shop_validation
        self._order_item_reader = order_item_reader
        self._order_reader = order_reader
        self._commiter = commiter

    async def __call__(self, data: EditOrderItemQuantityInputData) -> None:
        if data.shop_id:
            await self._shop_validation.check_shop(ShopId(data.shop_id))

        order_item = await self._order_item_reader.by_id(
            OrderItemId(data.order_item_id)
        )

        if not order_item:
            raise OrderItemNotFoundError(data.order_item_id)

        order = await self._order_reader.by_id(order_item.order_id)

        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserNotFoundError()

        await self._access_service.ensure_can_edit_order(actor.user_id, order)

        order_item.amount = order_item.amount.edit_quantity(data.quantity)

        order_items = await self._order_item_reader.by_order_id(order.order_id)

        order.total_price = OrderTotalPrice(total_price(order_items))

        logging.info(
            "Order item with id=%s change his quantity to %s",
            data.order_item_id,
            data.quantity,
        )

        await self._commiter.commit()
