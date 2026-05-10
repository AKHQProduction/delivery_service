from dataclasses import dataclass

from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderDetailReadModel,
)
from backend.application.services.recurring_order_planning_read import (
    RecurringOrderPlanningRead,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.idp import IdentityProvider


@dataclass(frozen=True)
class GetRecurringOrderQuery:
    recurring_order_id: RecurringOrderId


class GetRecurringOrderQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_planning_read: RecurringOrderPlanningRead,
    ) -> None:
        self._idp = idp
        self._recurring_order_planning_read = recurring_order_planning_read

    async def handle(
        self, query: GetRecurringOrderQuery
    ) -> RecurringOrderDetailReadModel:
        current_user = await self._idp.current_user()
        return await self._recurring_order_planning_read.detail(
            current_user, query.recurring_order_id
        )
