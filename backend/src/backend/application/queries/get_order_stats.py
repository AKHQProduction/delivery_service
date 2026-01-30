import datetime
import logging
from dataclasses import dataclass

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderGateway,
    TimeSlotFilter,
)
from backend.application.interfaces.gateways.time_slot_gateway import (
    TimeSlotGateway,
)
from backend.application.vars import PaymentMethod

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetOrderStatsQuery:
    start_date: datetime.date
    end_date: datetime.date


@dataclass(frozen=True)
class OrderStatsByCategory:
    name: str
    quantity: int


@dataclass(frozen=True)
class OrderStatsByPaymentMethod:
    method: PaymentMethod
    orders_sum: int


@dataclass(frozen=True)
class OrderStatsByTimeSlot:
    time_slot: str
    total: int


@dataclass(frozen=True)
class GetOrderStatsResponse:
    total_orders: int
    total_orders_sum: int
    time_slot_stats: list[OrderStatsByTimeSlot]
    category_stats: list[OrderStatsByCategory]
    payment_method_stats: list[OrderStatsByPaymentMethod]


class GetOrderStatsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: OrderGateway,
        time_slot_gateway: TimeSlotGateway,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway
        self._time_slot_gateway = time_slot_gateway

    async def handle(self, query: GetOrderStatsQuery) -> GetOrderStatsResponse:
        current_user = await self._idp.current_user()

        logger.info(
            "Fetching order stats for shop_id=%s, start_date=%s, end_date=%s",
            current_user.shop_id,
            query.start_date,
            query.end_date,
        )

        time_slots = await self._time_slot_gateway.load_by_shop(
            current_user.shop_id
        )
        time_slots_filter = [
            TimeSlotFilter(
                start_time=datetime.time.fromisoformat(slot.start_time),
                end_time=datetime.time.fromisoformat(slot.end_time),
            )
            for slot in time_slots
        ]

        stats = await self._order_gateway.get_stats(
            filters=GetOrdersFilters(
                shop_id=current_user.shop_id,
                start_date=query.start_date,
                end_date=query.end_date,
            ),
            time_slots_filter=time_slots_filter,
        )

        logger.info(
            "Order stats retrieved: total_orders=%d, total_sum=%d",
            stats.total_orders,
            stats.total_orders_sum,
        )

        return GetOrderStatsResponse(
            total_orders=stats.total_orders,
            total_orders_sum=stats.total_orders_sum,
            time_slot_stats=[
                OrderStatsByTimeSlot(
                    time_slot=slot.time_slot,
                    total=slot.total,
                )
                for slot in stats.time_slot_stats
            ],
            category_stats=[
                OrderStatsByCategory(name=cat.name, quantity=cat.quantity)
                for cat in stats.category_stats
            ],
            payment_method_stats=[
                OrderStatsByPaymentMethod(
                    method=pm.method, orders_sum=pm.orders_sum
                )
                for pm in stats.payment_method_stats
            ],
        )
