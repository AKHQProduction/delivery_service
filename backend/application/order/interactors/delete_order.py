import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.order.errors import OrderNotFoundError
from application.order.gateway import OrderReader, OrderSaver
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopReader
from application.user.errors import UserNotFoundError
from entities.order.models import OrderId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class DeleteOrderInputData:
    order_id: int
    shop_id: int | None = None


class DeleteOrder(Interactor[DeleteOrderInputData, None]):
    def __init__(
        self,
        shop_reader: ShopReader,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        order_reader: OrderReader,
        order_saver: OrderSaver,
        commiter: Commiter,
    ):
        self._shop_reader = shop_reader
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._order_reader = order_reader
        self._order_saver = order_saver
        self._commiter = commiter

    async def __call__(self, data: DeleteOrderInputData) -> None:
        if data.shop_id:
            shop = await self._shop_reader.by_id(ShopId(data.shop_id))

            if not shop:
                raise ShopNotFoundError(data.shop_id)

            if not shop.is_active:
                raise ShopIsNotActiveError(data.shop_id)

        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserNotFoundError()

        order = await self._order_reader.by_id(OrderId(data.order_id))

        if not order:
            raise OrderNotFoundError(data.order_id)

        await self._access_service.ensure_can_delete_order(
            actor.user_id, order
        )

        await self._order_saver.delete(order)

        await self._commiter.commit()

        logging.info("Order with id=%s was deleted", data.order_id)
