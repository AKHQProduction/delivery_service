import logging
from dataclasses import dataclass

from application.common.errors.order import OrderNotFoundError
from application.common.identity_provider import IdentityProvider
from application.common.persistence.order import OrderReader
from application.common.persistence.shop import ShopGateway
from application.common.persistence.view_models import OrderView
from application.common.validators import validate_shop, validate_user
from entities.order.models import OrderId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetOrderQuery:
    order_id: int
    shop_id: int | None = None


@dataclass
class GetOrderQueryHandler:
    identity_provider: IdentityProvider
    order_reader: OrderReader
    shop_gateway: ShopGateway

    async def __call__(self, query: GetOrderQuery) -> OrderView:
        if query.shop_id:
            shop = await self.shop_gateway.load_with_id(ShopId(query.shop_id))
            validate_shop(shop)

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        order_id = OrderId(query.order_id)
        order_view = await self.order_reader.read_with_id(order_id)
        if not order_view:
            raise OrderNotFoundError(order_id)

        logging.info("Get order with id=%s", order_id)

        return order_view
