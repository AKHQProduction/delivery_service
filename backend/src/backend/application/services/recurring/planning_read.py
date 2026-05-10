import logging

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

logger = logging.getLogger(__name__)


class RecurringOrderPlanningRead:
    def __init__(
        self, recurring_order_read_gateway: SQLAlchemyRecurringOrderReadGateway
    ) -> None:
        self._recurring_order_read_gateway = recurring_order_read_gateway

    async def list(
        self, current_user: CurrentUserDTO, filters: RecurringOrderFilters
    ) -> list[RecurringOrderReadModel]:
        logger.debug(
            "Reading recurring order planning list: shop_id=%s filters=%s",
            current_user.shop_id,
            filters,
        )
        rows = await self._recurring_order_read_gateway.read_all(
            current_user.shop_id, filters
        )
        logger.info(
            "Recurring order planning list read: shop_id=%s rows=%d",
            current_user.shop_id,
            len(rows),
        )
        return rows

    async def detail(
        self,
        current_user: CurrentUserDTO,
        recurring_order_id: RecurringOrderId,
    ) -> RecurringOrderDetailReadModel:
        logger.debug(
            "Reading recurring order planning detail: "
            "recurring_order_id=%s shop_id=%s",
            recurring_order_id,
            current_user.shop_id,
        )
        return ensure_exists(
            await self._recurring_order_read_gateway.read(
                recurring_order_id, current_user.shop_id
            ),
            "RecurringOrder",
        )
