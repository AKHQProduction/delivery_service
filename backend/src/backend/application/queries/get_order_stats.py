import datetime
import logging
from dataclasses import dataclass

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderGateway,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetOrderStatsQuery:
    date: datetime.date


@dataclass(frozen=True)
class GetOrderStatsResponse:
    total_orders: int
    total_orders_in_first_half: int
    total_orders_in_second_half: int
    total_orders_sum: int


class GetOrderStatsQueryHandler:
    def __init__(
        self, idp: IdentityProvider, order_gateway: OrderGateway
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway

    async def handle(self, query: GetOrderStatsQuery) -> GetOrderStatsResponse:
        current_user = await self._idp.current_user()

        logger.info(
            "Fetching order stats for shop_id=%s, date=%s",
            current_user.shop_id,
            query.date,
        )

        stats = await self._order_gateway.get_stats(
            filters=GetOrdersFilters(
                shop_id=current_user.shop_id,
                delivery_date=query.date,
            )
        )

        logger.info(
            "Order stats retrieved: total_orders=%d, first_half=%d, "
            "second_half=%d, total_sum=%d",
            stats.total_orders,
            stats.total_orders_in_first_half,
            stats.total_orders_in_second_half,
            stats.total_orders_sum,
        )

        return GetOrderStatsResponse(
            total_orders=stats.total_orders,
            total_orders_in_first_half=stats.total_orders_in_first_half,
            total_orders_in_second_half=stats.total_orders_in_second_half,
            total_orders_sum=stats.total_orders_sum,
        )
