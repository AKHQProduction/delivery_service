from dataclasses import dataclass

from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderFilters,
    RecurringOrderReadModel,
)
from backend.application.vars import RecurringOrderStatus, ScheduleType
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)


@dataclass(frozen=True)
class GetRecurringOrdersQuery:
    client_name: str | None = None
    status: RecurringOrderStatus | None = None
    schedule_type: ScheduleType | None = None
    weekday: int | None = None
    month_day: int | None = None


class GetRecurringOrdersQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway

    async def handle(
        self, query: GetRecurringOrdersQuery
    ) -> list[RecurringOrderReadModel]:
        current_user = await self._idp.current_user()
        return await self._recurring_order_gateway.read_all(
            current_user.shop_id,
            RecurringOrderFilters(
                client_name=query.client_name,
                status=query.status,
                schedule_type=query.schedule_type,
                weekday=query.weekday,
                month_day=query.month_day,
            ),
        )
