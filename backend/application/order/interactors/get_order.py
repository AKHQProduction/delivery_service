from dataclasses import dataclass
from decimal import Decimal

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.order.gateway import OrderItemReader, OrderReader
from application.order.shop_validate import ShopValidationService
from application.user.errors import UserIsNotExistError
from entities.order.models import OrderId, OrderItem, OrderStatus
from entities.shop.models import ShopId


@dataclass(frozen=True)
class GetOrderInputData:
    order_id: int
    shop_id: int | None = None


@dataclass(frozen=True)
class GetOrderOutputData:
    status: OrderStatus
    total_price: Decimal
    items: list[OrderItem]


class GetOrder(Interactor[GetOrderInputData, GetOrderOutputData]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        order_reader: OrderReader,
        order_item_reader: OrderItemReader,
        shop_validation: ShopValidationService,
    ):
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._order_reader = order_reader
        self._order_item_reader = order_item_reader
        self._shop_validation = shop_validation

    async def __call__(self, data: GetOrderInputData) -> GetOrderOutputData:
        if data.shop_id:
            await self._shop_validation.check_shop(ShopId(data.shop_id))

        actor = await self._identity_provider.get_user()

        if not actor:
            raise UserIsNotExistError()

        order = await self._order_reader.by_id(OrderId(data.order_id))

        await self._access_service.ensure_can_get_order(actor.user_id, order)

        order_items = await self._order_item_reader.by_order_id(
            OrderId(data.order_id)
        )

        return GetOrderOutputData(
            status=order.status,
            total_price=order.total_price.price,
            items=order_items,
        )
