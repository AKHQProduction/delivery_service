from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderDetailReadModel,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)


@dataclass(frozen=True)
class GetRecurringOrderQuery:
    recurring_order_id: RecurringOrderId


class GetRecurringOrderQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway

    async def handle(
        self, query: GetRecurringOrderQuery
    ) -> RecurringOrderDetailReadModel:
        current_user = await self._idp.current_user()
        return ensure_exists(
            await self._recurring_order_gateway.read(
                query.recurring_order_id, current_user.shop_id
            ),
            "RecurringOrder",
        )
