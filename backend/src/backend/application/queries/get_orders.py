from dataclasses import dataclass
from datetime import date, time

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.order_gateway import (
    GetOrdersFilters,
    OrderReadModel,
    OrderSummaryReadModel,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyOrderGateway


@dataclass(frozen=True)
class GetOrdersQuery:
    pagination: Pagination
    start_date: date | None = None
    end_date: date | None = None
    delivery_start_time: time | None = None
    client_name: str | None = None


@dataclass(frozen=True)
class GetOrderSummaryQuery:
    start_date: date | None = None
    end_date: date | None = None
    delivery_start_time: time | None = None
    client_name: str | None = None


class GetOrdersQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_gateway: SQLAlchemyOrderGateway,
    ) -> None:
        self._idp = idp
        self._order_gateway = order_gateway

    async def handle(self, query: GetOrdersQuery) -> list[OrderReadModel]:
        current_user = await self._idp.current_user()

        return await self._order_gateway.read_all(
            filters=GetOrdersFilters(
                shop_id=current_user.shop_id,
                start_date=query.start_date,
                end_date=query.end_date,
                delivery_start_time=query.delivery_start_time,
                client_name=query.client_name,
            ),
            pagination=query.pagination,
        )

    async def summary(
        self, query: GetOrderSummaryQuery
    ) -> OrderSummaryReadModel:
        current_user = await self._idp.current_user()

        return await self._order_gateway.read_summary(
            filters=GetOrdersFilters(
                shop_id=current_user.shop_id,
                start_date=query.start_date,
                end_date=query.end_date,
                delivery_start_time=query.delivery_start_time,
                client_name=query.client_name,
            ),
        )
