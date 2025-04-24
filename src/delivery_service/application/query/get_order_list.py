import asyncio
import logging
from dataclasses import dataclass
from datetime import date

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.file_manager import FileManager
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.common.order_mapper import (
    map_order_to_read_model,
)
from delivery_service.application.query.ports.address_gateway import (
    AddressGateway,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.application.query.ports.order_gateway import (
    OrderReadModel,
)
from delivery_service.domain.orders.order import DeliveryPreference, Order
from delivery_service.domain.orders.order_list_collector import (
    OrderListCollector,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shops.repository import ShopRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MakeOrderListRequest(TelegramRequest):
    selected_day: date


class GetOrderListHandler(
    RequestHandler[
        MakeOrderListRequest, dict[DeliveryPreference, bytes] | None
    ]
):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_repository: ShopRepository,
        service: OrderListCollector,
        customer_gateway: CustomerGateway,
        address_gateway: AddressGateway,
        file_manager: FileManager,
    ) -> None:
        self._idp = idp
        self._shop_repository = shop_repository
        self._order_service = service
        self._customer_gateway = customer_gateway
        self._address_gateway = address_gateway
        self._file_manager = file_manager

    async def handle(
        self, request: MakeOrderListRequest
    ) -> dict[DeliveryPreference, bytes] | None:
        logger.info("Request to get order list")
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise AccessDeniedError()

        collected_orders = (
            await self._order_service.collect_orders_by_proximity(
                shop, request.selected_day
            )
        )
        if not collected_orders:
            return None

        result: dict[DeliveryPreference, list[OrderReadModel]] = {}

        for preference, orders in collected_orders.items():
            tasks = [self._map_order(order) for order in orders]
            mapped = await asyncio.gather(*tasks)
            mapped_orders = [item for item in mapped if item is not None]

            if mapped_orders:
                result[preference] = mapped_orders

        if not result:
            return None

        return self._file_manager.create_order_files(result)

    async def _map_order(self, order: Order) -> OrderReadModel | None:
        customer_task = asyncio.create_task(
            self._customer_gateway.read_with_id(order.client_id)
        )
        address_task = asyncio.create_task(
            self._address_gateway.read_with_id(order.address_reference)
        )

        customer, address = await asyncio.gather(customer_task, address_task)
        if not customer or not address:
            logger.debug(
                "Customer %s or address %s not found, continue...",
                order.client_id,
                order.address_reference,
            )
            return None
        return map_order_to_read_model(
            order=order, customer=customer, address=address
        )
