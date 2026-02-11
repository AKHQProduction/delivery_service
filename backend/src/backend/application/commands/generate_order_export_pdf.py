import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, time

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.services.route_optimizer import RouteOptimizer
from backend.application.vars import OrderId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.pdf import ReportLabOrdersPDFGenerator
from backend.infrastructure.persistence.gateways import (
    RedisPDFStorage,
    SQLAlchemyOrderGateway,
    SQLAlchemyShopGateway,
)
from backend.infrastructure.persistence.tables.orders import Order

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerateOrderExportPDFCommand:
    delivery_date: date


@dataclass(frozen=True)
class GenerateOrderExportPDFResult:
    file_id: str
    filename: str


class GenerateOrderExportPDFCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        shop_gateway: SQLAlchemyShopGateway,
        pdf_generator: ReportLabOrdersPDFGenerator,
        pdf_storage: RedisPDFStorage,
        route_optimizer: RouteOptimizer,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._shop_gateway = shop_gateway
        self._pdf_generator = pdf_generator
        self._pdf_storage = pdf_storage
        self._route_optimizer = route_optimizer

    async def handle(
        self, command: GenerateOrderExportPDFCommand
    ) -> GenerateOrderExportPDFResult:
        logger.info(
            "Generating orders PDF for date: %s", command.delivery_date
        )

        current_user = await self._idp.current_user()

        shop_id = current_user.shop_id
        if not shop_id:
            logger.warning("User %s has no shop_id", current_user.user_id)
            raise AccessDeniedError

        shop = await self._shop_gateway.load_shop(shop_id)
        if not shop:
            logger.warning("Shop not found: shop_id=%s", shop_id)
            raise EntityNotFoundError(entity="Shop")

        orders = await self._order_gateway.load_by_date(
            shop_id, command.delivery_date
        )

        logger.info(
            "Found %d orders for date %s, shop %s",
            len(orders),
            command.delivery_date,
            shop_id,
        )

        shop_coords = CoordinatesDTO.build(shop.latitude, shop.longitude)
        if shop_coords:
            orders = await self._optimize_orders(orders, shop_coords)

        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(
            None,
            self._pdf_generator.handle,
            orders,
            command.delivery_date,
            shop.name,
        )

        filename = f"orders_{command.delivery_date.isoformat()}.pdf"
        file_id = await self._pdf_storage.save(pdf_bytes, filename)

        logger.info(
            "Successfully generated PDF for date %s, shop %s (file_id=%s)",
            command.delivery_date,
            shop_id,
            file_id,
        )

        return GenerateOrderExportPDFResult(file_id=file_id, filename=filename)

    async def _optimize_orders(
        self,
        orders: list[Order],
        shop_coords: CoordinatesDTO,
    ) -> list[Order]:
        slots: dict[tuple[time, time], list[Order]] = defaultdict(list)
        for order in orders:
            key = (order.delivery_start_time, order.delivery_end_time)
            slots[key].append(order)

        result: list[Order] = []
        for key in sorted(slots):
            slot_orders = slots[key]
            optimized_ids = await self._route_optimizer.compute(
                shop_coords, slot_orders
            )
            if optimized_ids:
                result.extend(
                    self._apply_route_order(slot_orders, optimized_ids)
                )
            else:
                result.extend(slot_orders)

        return result

    @staticmethod
    def _apply_route_order(
        orders: list[Order], order_ids: list[OrderId]
    ) -> list[Order]:
        orders_map = {o.id: o for o in orders}
        ordered = [orders_map[oid] for oid in order_ids if oid in orders_map]
        seen = set(order_ids)
        ordered.extend(o for o in orders if o.id not in seen)
        return ordered
