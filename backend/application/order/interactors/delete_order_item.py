import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.order.errors import (
    OrderItemNotFoundError,
    OrderNotFoundError,
)
from application.order.gateway import (
    OrderItemReader,
    OrderItemSaver,
    OrderReader,
    OrderSaver,
)
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopReader
from application.user.errors import UserNotFoundError
from entities.order.models import OrderItemId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class DeleteOrderItemInputData:
    order_item_id: int
    shop_id: int | None = None


class DeleteOrderItem(Interactor[DeleteOrderItemInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        shop_reader: ShopReader,
        order_item_reader: OrderItemReader,
        order_item_saver: OrderItemSaver,
        order_reader: OrderReader,
        order_saver: OrderSaver,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._shop_reader = shop_reader
        self._order_item_reader = order_item_reader
        self._order_item_saver = order_item_saver
        self._order_reader = order_reader
        self._order_saver = order_saver
        self._commiter = commiter

    async def __call__(self, data: DeleteOrderItemInputData) -> None:
        if data.shop_id:
            shop = await self._shop_reader.by_id(ShopId(data.shop_id))

            if not shop:
                raise ShopNotFoundError(data.shop_id)

            if not shop.is_active:
                raise ShopIsNotActiveError(data.shop_id)

        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserNotFoundError()

        order_item = await self._order_item_reader.by_id(
            OrderItemId(data.order_item_id)
        )

        if not order_item:
            raise OrderItemNotFoundError(data.order_item_id)

        order = await self._order_reader.by_id(order_item.order_id)

        if not order:
            raise OrderNotFoundError(order_item.order_id)

        await self._access_service.ensure_can_edit_order(actor.user_id, order)

        await self._order_item_saver.delete(order_item)

        logging.info(
            "Order item with id=%s was deleted", order_item.order_item_id
        )

        order_items = await self._order_item_reader.by_order_id(order.order_id)

        if len(order_items) == 0:
            await self._order_saver.delete(order)
            logging.info("Order with id=%s was deleted", order.order_id)

        await self._commiter.commit()
