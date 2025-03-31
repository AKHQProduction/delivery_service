from datetime import date

from entities.common.tracker import Tracker
from entities.common.vo import Price, Quantity
from entities.order.models import (
    DeliveryPreference,
    Order,
    OrderId,
    OrderItem,
    OrderItemId,
    OrderStatus,
)
from entities.shop.models import Shop
from entities.user.models import UserId


class OrderService:
    def __init__(self, tracker: Tracker) -> None:
        self.tracker = tracker

    def create_order(
        self,
        user_id: UserId,
        shop: Shop,
        bottle_to_exchange: Quantity,
        delivery_preference: DeliveryPreference,
        delivery_date: date,
    ) -> Order:
        if not shop.days_off.can_receive_orders(delivery_date):
            raise ValueError()

        new_order = Order(
            oid=None,
            user_id=user_id,
            shop_id=shop.oid,
            status=OrderStatus.NEW,
            bottles_to_exchange=bottle_to_exchange,
            delivery_preference=delivery_preference,
            delivery_date=delivery_date,
        )

        self.tracker.add_one(new_order)

        return new_order

    @staticmethod
    def create_order_item(
        order_id: OrderId, title: str, quantity: Quantity, price: Price
    ) -> OrderItem:
        return OrderItem(
            oid=None,
            order_id=order_id,
            order_item_title=title,
            quantity=quantity,
            price_per_item=price,
        )

    def add_order_items(self, order: Order, order_items: list[OrderItem]):
        order.order_items.extend(order_items)
        self.tracker.add_many(order_items)

    async def delete_order(self, order: Order):
        await self.tracker.delete(order)

    async def remove_order_item(
        self, order: Order, order_item_id: OrderItemId
    ):
        order_item = self._find_order_item(order_item_id, order)

        order.order_items.remove(order_item)
        await self.tracker.delete(order_item)

        if len(order.order_items) == 0:
            await self.tracker.delete(order)

    def change_item_quantity(
        self, new_quantity: int, order: Order, order_item_id: OrderItemId
    ):
        order_item = self._find_order_item(order_item_id, order)

        order_item.quantity = Quantity(new_quantity)

    @staticmethod
    def _find_order_item(
        order_item_id: OrderItemId, order: Order
    ) -> OrderItem | None:
        return next(
            (item for item in order.order_items if item.oid == order_item_id),
            None,
        )
