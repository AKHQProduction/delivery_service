from backend.application.common import ensure_exists
from backend.application.dto.gateways.recurring_order_gateway import (
    RecurringOrderDetailReadModel,
    RecurringOrderFilters,
    RecurringOrderReadModel,
)
from backend.application.dto.idp import CurrentUserDTO
from backend.application.vars import RecurringOrderId
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderReadGateway,
)


class RecurringOrderPlanningRead:
    def __init__(
        self, recurring_order_read_gateway: SQLAlchemyRecurringOrderReadGateway
    ) -> None:
        self._recurring_order_read_gateway = recurring_order_read_gateway

    async def list(
        self, current_user: CurrentUserDTO, filters: RecurringOrderFilters
    ) -> list[RecurringOrderReadModel]:
        return await self._recurring_order_read_gateway.read_all(
            current_user.shop_id, filters
        )

    async def detail(
        self,
        current_user: CurrentUserDTO,
        recurring_order_id: RecurringOrderId,
    ) -> RecurringOrderDetailReadModel:
        return ensure_exists(
            await self._recurring_order_read_gateway.read(
                recurring_order_id, current_user.shop_id
            ),
            "RecurringOrder",
        )
