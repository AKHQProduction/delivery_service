import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, time

from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.services.route_builder import sort_orders_by_sequence
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.vars import (
    ExportDocType,
    OrderId,
    RoutingMode,
    TimeSlotId,
)
from backend.infrastructure.idp import (
    IdentityProvider,
)
from backend.infrastructure.pdf import ReportLabOrdersPDFGenerator
from backend.infrastructure.persistence.gateways import (
    RedisFileStorage,
    SQLAlchemyOrderGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables import Shop
from backend.infrastructure.persistence.tables.orders import Order

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerateOrderExportPDFCommand:
    delivery_date: date
    doc_type: ExportDocType
    time_slot_id: TimeSlotId | None = None
    routing_mode: RoutingMode = RoutingMode.NONE


@dataclass(frozen=True)
class GenerateOrderExportPDFResult:
    file_id: str
    filename: str


class GenerateOrderExportPDFCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
        shop_gateway: SQLAlchemyShopGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        pdf_generator: ReportLabOrdersPDFGenerator,
        pdf_storage: RedisFileStorage,
        route_optimizer: RouteOptimizer,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._shop_gateway = shop_gateway
        self._time_slot_gateway = time_slot_gateway
        self._route_plan_gateway = route_plan_gateway
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

        start_time = None
        end_time = None
        if command.time_slot_id:
            time_slot = await self._time_slot_gateway.load(
                command.time_slot_id
            )
            if not time_slot:
                raise EntityNotFoundError(entity="TimeSlot")
            start_time = time_slot.start_time
            end_time = time_slot.end_time

        orders = await self._order_gateway.load_by_date(
            shop_id, command.delivery_date, start_time, end_time
        )

        logger.info(
            "Found %d orders for date %s, shop %s",
            len(orders),
            command.delivery_date,
            shop_id,
        )

        loop = asyncio.get_running_loop()

        if command.doc_type == ExportDocType.ORDER_LIST:
            if command.routing_mode == RoutingMode.OPTIMIZED:
                orders = await self._sort_by_route(
                    orders,
                    shop,
                    command.delivery_date,
                    command.time_slot_id,
                )

            pdf_bytes = await loop.run_in_executor(
                None,
                self._pdf_generator.build_order_list,
                orders,
                command.delivery_date,
            )
            filename = f"orders_{command.delivery_date.isoformat()}.pdf"
        else:
            pdf_bytes = await loop.run_in_executor(
                None,
                self._pdf_generator.build_statistics,
                orders,
                command.delivery_date,
                shop.name,
            )
            filename = f"statistics_{command.delivery_date.isoformat()}.pdf"
        file_id = await self._pdf_storage.save(pdf_bytes, filename)

        logger.info(
            "Successfully generated PDF for date %s, shop %s (file_id=%s)",
            command.delivery_date,
            shop_id,
            file_id,
        )

        return GenerateOrderExportPDFResult(file_id=file_id, filename=filename)

    async def _sort_by_route(
        self,
        orders: list[Order],
        shop: Shop,
        delivery_date: date,
        time_slot_id: TimeSlotId | None,
    ) -> list[Order]:
        route_plan = await self._route_plan_gateway.load_by_date(
            shop.id,
            delivery_date,
            time_slot_id,
        )

        if route_plan:
            routable, unroutable = sort_orders_by_sequence(
                orders,
                route_plan.order_sequence,
            )
            return [*routable, *unroutable]

        shop_coords = CoordinatesDTO.build(shop.latitude, shop.longitude)
        if shop_coords:
            return await self._optimize_orders(orders, shop_coords)
        return orders

    async def _optimize_orders(
        self,
        orders: list[Order],
        shop_coords: CoordinatesDTO,
    ) -> list[Order]:
        slots: dict[tuple[time, time], list[Order]] = defaultdict(list)
        for order in orders:
            key = (order.delivery_start_time, order.delivery_end_time)
            slots[key].append(order)

        sorted_keys = sorted(slots)
        optimized_ids_list = await asyncio.gather(
            *(
                self._route_optimizer.compute(shop_coords, slots[key])
                for key in sorted_keys
            )
        )

        result: list[Order] = []
        for key, optimized_ids in zip(
            sorted_keys, optimized_ids_list, strict=True
        ):
            slot_orders = slots[key]
            if optimized_ids:
                result.extend(
                    self._apply_route_order(slot_orders, optimized_ids)
                )
            else:
                logger.warning(
                    "Route optimization failed for slot %s-%s (%d orders)",
                    key[0],
                    key[1],
                    len(slot_orders),
                )
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
