import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.order import OrderGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import (
    validate_order_with_item,
    validate_shop,
    validate_user,
)
from entities.order.models import OrderItemId
from entities.order.service import OrderService
from entities.shop.models import ShopId


@dataclass(frozen=True)
class EditOrderItemQuantityCommand:
    order_item_id: int
    quantity: int
    shop_id: int | None = None


@dataclass
class EditOrderItemQuantityCommandHandler:
    identity_provider: IdentityProvider
    access_service: AccessService
    shop_gateway: ShopGateway
    order_gateway: OrderGateway
    order_service: OrderService
    transaction_manager: TransactionManager

    async def __call__(self, command: EditOrderItemQuantityCommand) -> None:
        if command.shop_id:
            shop_id = ShopId(command.shop_id)

            shop = await self.shop_gateway.load_with_id(shop_id)
            validate_shop(shop)

        order_item_id = OrderItemId(command.order_item_id)
        order = await self.order_gateway.load_with_item_id(order_item_id)
        validate_order_with_item(order, order_item_id)

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        await self.access_service.ensure_can_edit_order(actor.oid, order)

        self.order_service.change_item_quantity(
            new_quantity=command.quantity,
            order_item_id=order_item_id,
            order=order,
        )

        logging.info(
            "Order item with id=%s change his quantity to %s",
            command.order_item_id,
            command.quantity,
        )

        await self.transaction_manager.commit()
