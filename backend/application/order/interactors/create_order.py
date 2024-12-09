import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.transaction_manager import TransactionManager
from application.goods.gateway import GoodsReader
from application.order.gateway import OrderItemSaver, OrderSaver
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import OldShopGateway
from application.user.errors import UserNotFoundError
from entities.order.models import (
    DeliveryPreference,
    Order,
    OrderItem,
    OrderStatus,
)
from entities.order.service import total_price
from entities.order.value_objects import (
    BottlesToExchange,
    OrderItemAmount,
    OrderTotalPrice,
)
from entities.shop.models import ShopId


@dataclass(frozen=True)
class OrderItemData:
    quantity: int
    price: Decimal
    title: str


@dataclass(frozen=True)
class CreateOrderInputData:
    shop_id: int
    bottles_to_exchange: int
    delivery_preference: DeliveryPreference
    items: list[OrderItemData]
    delivery_date: date


@dataclass(frozen=True)
class CreateOrderOutputData:
    order_id: int


class CreateOrder(Interactor[CreateOrderInputData, CreateOrderOutputData]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: OldShopGateway,
        order_saver: OrderSaver,
        order_items_saver: OrderItemSaver,
        goods_reader: GoodsReader,
        commiter: TransactionManager,
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
        if not shop:
            raise ShopNotFoundError(shop_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(shop_id)

        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        order = Order(
            order_id=None,
            user_id=actor.user_id,
            shop_id=shop_id,
            status=OrderStatus.NEW,
            total_price=OrderTotalPrice(Decimal(0)),
            bottles_to_exchange=BottlesToExchange(data.bottles_to_exchange),
            delivery_preference=data.delivery_preference,
            delivery_date=data.delivery_date,
        )

        await self._order_saver.save(order)

        order_items = [
            OrderItem(
                order_id=order.order_id,
                order_item_id=None,
                order_item_title=item.title,
                amount=OrderItemAmount(
                    quantity=item.quantity, price_per_item=item.price
                ),
            )
            for item in data.items
        ]

        order.total_price = OrderTotalPrice(total_price(order_items))

        await self._order_item_saver.save_items(order_items)

        await self._commiter.commit()

        logging.info(
            "Create order with id=%s, items=%s", order.order_id, order_items
        )

        return CreateOrderOutputData(order_id=order.order_id)
