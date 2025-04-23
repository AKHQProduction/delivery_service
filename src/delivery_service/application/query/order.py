import logging
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
from delivery_service.application.query.common.order_mapper import (
    map_order_to_read_model,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.application.query.ports.order_gateway import (
    OrderReadModel,
)
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.orders.repository import (
    OrderRepository,
    OrderRepositoryFilters,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.staff.repository import StaffMemberRepository

logger = logging.getLogger(__name__)


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
        logger.info("Request to get all staff shop orders")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        shop_orders = await self._order_repository.load_many(
            OrderRepositoryFilters(shop_id=staff_member.from_shop)
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

            orders.append(map_order_to_read_model(order, customer))

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
        logger.info("Request to concrete shop order")

        order = await self._order_repository.load_with_id(request.order_id)
        if not order:
            raise OrderNotFoundError()
        customer = await self._customer_gateway.read_with_id(order.client_id)
        if not customer:
            raise CustomerNotFoundError()

        return map_order_to_read_model(order, customer)
