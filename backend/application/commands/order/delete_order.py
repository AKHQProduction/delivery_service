import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.order import OrderGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import (
    validate_order,
    validate_shop,
    validate_user,
)
from entities.order.models import OrderId
from entities.order.service import OrderService
from entities.shop.models import ShopId


@dataclass(frozen=True)
class DeleteOrderInputData:
    order_id: int
    shop_id: int | None = None


@dataclass
class DeleteOrder:
    shop_gateway: ShopGateway
    identity_provider: IdentityProvider
    access_service: AccessService
    order_gateway: OrderGateway
    order_service: OrderService
    transaction_manager: TransactionManager

    async def __call__(self, command: DeleteOrderInputData) -> None:
        shop_id = ShopId(command.shop_id)
        order_id = OrderId(command.order_id)

        if command.shop_id:
            shop = await self.shop_gateway.load_with_id(shop_id)
            validate_shop(shop)

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        order = await self.order_gateway.load_with_id(order_id)
        validate_order(order, order_id)

        await self.access_service.ensure_can_delete_order(actor.oid, order)

        await self.order_service.delete_order(order)

        await self.transaction_manager.commit()

        logging.info("Order with id=%s was deleted", command.order_id)
