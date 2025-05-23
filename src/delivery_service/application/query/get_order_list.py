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
from delivery_service.application.query.ports.order_list_collector import (
    OrderListCollector,
)
from delivery_service.application.query.ports.phone_number_gateway import (
    PhoneNumberGateway,
)
from delivery_service.domain.orders.order import Order
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shops.repository import ShopRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MakeOrderListRequest(TelegramRequest):
    selected_day: date


class GetOrderListHandler(RequestHandler[MakeOrderListRequest, bytes | None]):
    def __init__(
        self,
        idp: IdentityProvider,
        shop_repository: ShopRepository,
        service: OrderListCollector,
        customer_gateway: CustomerGateway,
        address_gateway: AddressGateway,
        phone_gateway: PhoneNumberGateway,
        file_manager: FileManager,
    ) -> None:
        self._idp = idp
        self._shop_repository = shop_repository
        self._order_service = service
        self._customer_gateway = customer_gateway
        self._address_gateway = address_gateway
        self._phone_gateway = phone_gateway
        self._file_manager = file_manager

    async def handle(self, request: MakeOrderListRequest) -> bytes | None:
        logger.info("Request to get order list")
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise AccessDeniedError()

        collected_orders = (
            await self._order_service.collect_orders_by_proximity(
                shop.id, shop.shop_coordinates, request.selected_day
            )
        )
        if not collected_orders:
            return None

        mapped_tasks = [
            asyncio.create_task(self._map_order(order))
            for order in collected_orders
        ]
        mapped_results = await asyncio.gather(*mapped_tasks)

        result: list[OrderReadModel] = [
            model for model in mapped_results if model is not None
        ]

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
