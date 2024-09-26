import logging
from dataclasses import dataclass
from decimal import Decimal

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.goods.gateway import GoodsReader
from application.order.gateway import OrderItemSaver, OrderSaver
from application.shop.errors import ShopIsNotActiveError
from application.shop.gateway import ShopReader
from entities.order.models import Order, OrderId, OrderItem, OrderStatus
from entities.order.service import total_price
from entities.order.value_objects import OrderItemAmount, OrderTotalPrice
from entities.shop.models import ShopId


@dataclass(frozen=True)
class OrderItemData:
    quantity: int
    price: Decimal
    title: str


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
        goods_reader: GoodsReader,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._order_saver = order_saver
        self._order_item_saver = order_items_saver
        self._goods_reader = goods_reader
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
            total_price=OrderTotalPrice(Decimal(0)),
        )

        await self._order_saver.save(order)

        order_items = self._create_order_items(
            order.order_id,
            data.items,
        )

        order.total_price = OrderTotalPrice(total_price(order_items))

        await self._order_item_saver.save_items(order_items)

        await self._commiter.commit()

        logging.info(
            "Create order with id=%s, items=%s", order.order_id, order_items
        )

        return CreateOrderOutputData(order_id=order.order_id)

    @staticmethod
    def _create_order_items(
        order_id: OrderId,
        items: list[OrderItemData],
    ) -> list[OrderItem]:
        return [
            OrderItem(
                order_id=order_id,
                order_item_id=None,
                order_item_title=item.title,
                amount=OrderItemAmount(
                    quantity=item.quantity, price_per_item=item.price
                ),
            )
            for item in items
        ]
