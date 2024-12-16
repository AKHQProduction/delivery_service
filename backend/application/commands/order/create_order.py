import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from application.common.identity_provider import IdentityProvider
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from entities.common.vo import Price, Quantity
from entities.order.models import (
    DeliveryPreference,
)
from entities.order.service import OrderService
from entities.shop.models import ShopId


@dataclass(frozen=True)
class OrderItemData:
    quantity: int
    price: Decimal
    title: str


@dataclass(frozen=True)
class CreateOrderCommand:
    shop_id: int
    bottles_to_exchange: int
    delivery_preference: DeliveryPreference
    items: list[OrderItemData]
    delivery_date: date


@dataclass(frozen=True)
class CreateOrderOutputData:
    order_id: int


@dataclass
class CreateOrderCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    order_service: OrderService
    transaction_manager: TransactionManager

    async def __call__(
        self, command: CreateOrderCommand
    ) -> CreateOrderOutputData:
        shop_id = ShopId(command.shop_id)

        shop = await self.shop_gateway.load_with_id(shop_id)
        validate_shop(shop)

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        bottle_to_exchange = Quantity(command.bottles_to_exchange)
        order = self.order_service.create_order(
            actor.oid,
            shop,
            bottle_to_exchange,
            command.delivery_preference,
            command.delivery_date,
        )

        await self.transaction_manager.flush()

        order_items = [
            self.order_service.create_order_item(
                order_id=order.oid,
                title=item.title,
                quantity=Quantity(item.quantity),
                price=Price(item.price),
            )
            for item in command.items
        ]

        self.order_service.add_order_items(order, order_items)

        await self.transaction_manager.commit()

        logging.info(
            "Create order with id=%s, items=%s", order.oid, order_items
        )

        return CreateOrderOutputData(order_id=order.oid)
