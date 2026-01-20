from dataclasses import dataclass
from datetime import date

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.order_gateway import (
    GetOrdersFilters,
    OrderGateway,
    OrderReadModel,
)
from backend.application.vars import TimePreference


@dataclass(frozen=True)
class GetOrdersQuery:
    pagination: Pagination
    start_date: date | None = None
    end_date: date | None = None
    time_preference: TimePreference | None = None
    client_name: str | None = None
    custom_id: str | None = None


class GetOrdersQueryHandler:
    def __init__(
        self, idp: IdentityProvider, order_gateway: OrderGateway
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
                time_preference=query.time_preference,
                client_name=query.client_name,
                custom_id=query.custom_id,
            ),
            pagination=Pagination(
                offset=query.pagination.offset,
                limit=query.pagination.limit,
                order=SortOrder.DESC,
            ),
        )
