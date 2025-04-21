from collections.abc import Sequence
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    CustomerNotFoundError,
    OrderNotFoundError,
)
from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.application.query.ports.order_gateway import (
    OrderLineReadModel,
    OrderReadModel,
)
from delivery_service.domain.orders.order import Order
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.orders.repository import OrderRepository
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.staff.repository import StaffMemberRepository


@dataclass(frozen=True)
class GetAllShopOrdersResponse:
    total: int
    orders: Sequence[OrderReadModel]


@dataclass(frozen=True)
class GetAllShopOrdersRequest(TelegramRequest[GetAllShopOrdersResponse]):
    pass


class GetAllShopOrdersHandler(
    RequestHandler[GetAllShopOrdersRequest, GetAllShopOrdersResponse]
):
    def __init__(
        self,
        idp: IdentityProvider,
        staff_repository: StaffMemberRepository,
        order_repository: OrderRepository,
        customer_gateway: CustomerGateway,
    ) -> None:
        self._idp = idp
        self._staff_repository = staff_repository
        self._order_repository = order_repository
        self._customer_gateway = customer_gateway

    async def handle(
        self, request: GetAllShopOrdersRequest
    ) -> GetAllShopOrdersResponse:
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        shop_orders = await self._order_repository.load_many_with_shop_id(
            shop_id=staff_member.from_shop
        )
        total_order = len(shop_orders)
        if total_order == 0:
            return GetAllShopOrdersResponse(total=total_order, orders=[])

        orders = []
        for order in shop_orders:
            customer = await self._customer_gateway.read_with_id(
                order.client_id
            )
            if not customer:
                continue

            orders.append(map_order_to_read_model(order, customer.full_name))

        return GetAllShopOrdersResponse(total=total_order, orders=orders)


@dataclass(frozen=True)
class GetShopOrderRequest(TelegramRequest[OrderReadModel]):
    order_id: OrderID


class GetShopOrderHandler(RequestHandler[GetShopOrderRequest, OrderReadModel]):
    def __init__(
        self,
        order_repository: OrderRepository,
        customer_gateway: CustomerGateway,
    ) -> None:
        self._order_repository = order_repository
        self._customer_gateway = customer_gateway

    async def handle(self, request: GetShopOrderRequest) -> OrderReadModel:
        order = await self._order_repository.load_with_id(request.order_id)
        if not order:
            raise OrderNotFoundError()
        customer = await self._customer_gateway.read_with_id(order.client_id)
        if not customer:
            raise CustomerNotFoundError()

        return map_order_to_read_model(order, customer.full_name)


def map_order_to_read_model(
    order: Order, customer_full_name: str
) -> OrderReadModel:
    return OrderReadModel(
        order_id=order.id,
        customer_full_name=customer_full_name,
        delivery_date=order.date,
        delivery_preference=order.delivery_time_preference,
        order_lines=[
            OrderLineReadModel(
                order_line_id=line.id,
                title=line.line_title,
                price_per_item=line.unit_price.value,
                quantity=line.total_quantity.value,
            )
            for line in order.order_lines
        ],
        total_order_price=order.total_order_price.value,
    )
