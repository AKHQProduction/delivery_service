from dataclasses import dataclass

from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderFilters,
    RecurringOrderReadModel,
)
from backend.application.services.recurring_order_planning_read import (
    RecurringOrderPlanningRead,
)
from backend.application.vars import (
    ClientId,
    RecurringOrderStatus,
    ScheduleType,
)
from backend.infrastructure.idp import IdentityProvider


@dataclass(frozen=True)
class GetRecurringOrdersQuery:
    client_id: ClientId | None = None
    client_name: str | None = None
    status: RecurringOrderStatus | None = None
    schedule_type: ScheduleType | None = None
    weekday: int | None = None
    month_day: int | None = None


class GetRecurringOrdersQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_planning_read: RecurringOrderPlanningRead,
    ) -> None:
        self._idp = idp
        self._recurring_order_planning_read = recurring_order_planning_read

    async def handle(
        self, query: GetRecurringOrdersQuery
    ) -> list[RecurringOrderReadModel]:
        current_user = await self._idp.current_user()
        return await self._recurring_order_planning_read.list(
            current_user,
            RecurringOrderFilters(
                client_id=query.client_id,
                client_name=query.client_name,
                status=query.status,
                schedule_type=query.schedule_type,
                weekday=query.weekday,
                month_day=query.month_day,
            ),
        )
