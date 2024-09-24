import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.order.gateway import OrderItemSaver, OrderSaver
from application.shop.errors import ShopIsNotActiveError
from application.shop.gateway import ShopReader
from entities.goods.models import GoodsId
from entities.order.models import Order, OrderItem, OrderStatus
from entities.order.value_objects import OrderItemQuantity
from entities.shop.models import ShopId


@dataclass(frozen=True)
class OrderItemData:
    goods_id: UUID
    quantity: int


@dataclass(frozen=True)
class CreateOrderInputData:
    shop_id: int
    items: list[OrderItemData]


@dataclass(frozen=True)
class CreateOrderOutputData:
    order_id: int


class CreateOrder(Interactor[CreateOrderInputData, CreateOrderOutputData]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: ShopReader,
        order_saver: OrderSaver,
        order_items_saver: OrderItemSaver,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._order_saver = order_saver
        self._order_item_saver = order_items_saver
        self._commiter = commiter

    async def __call__(
        self, data: CreateOrderInputData
    ) -> CreateOrderOutputData:
        shop_id = ShopId(data.shop_id)

        shop = await self._shop_reader.by_id(shop_id)

        if not shop.is_active:
            raise ShopIsNotActiveError(shop.shop_id)

        actor = await self._identity_provider.get_user()

        order = Order(
            order_id=None,
            user_id=actor.user_id,
            shop_id=shop_id,
            status=OrderStatus.NEW,
        )

        await self._order_saver.save(order)

        order_items = [
            OrderItem(
                order_item_id=None,
                order_id=order.order_id,
                goods_id=GoodsId(item.goods_id),
                quantity=OrderItemQuantity(item.quantity),
            )
            for item in data.items
        ]

        await self._order_item_saver.save_items(order_items)

        await self._commiter.commit()

        logging.info(
            "Create order with id=%s, items=%s", order.order_id, order_items
        )

        return CreateOrderOutputData(order_id=order.order_id)
