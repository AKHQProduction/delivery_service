import logging

from backend.application.common import ensure_exists
from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import RecurringOrderId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyRecurringOrderGateway,
)
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)

logger = logging.getLogger(__name__)


class RecurringOrderManagementContext:
    def __init__(
        self,
        idp: IdentityProvider,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._idp = idp
        self._recurring_order_gateway = recurring_order_gateway

    async def current_manager(self) -> CurrentUserDTO:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)
        logger.debug(
            "Resolved recurring order manager: user_id=%s shop_id=%s role=%s",
            current_user.user_id,
            current_user.shop_id,
            current_user.role,
        )
        return current_user

    async def load_owned(
        self,
        recurring_order_id: RecurringOrderId,
        current_user: CurrentUserDTO,
    ) -> RecurringOrder:
        logger.debug(
            "Loading owned recurring order: "
            "recurring_order_id=%s user_id=%s shop_id=%s",
            recurring_order_id,
            current_user.user_id,
            current_user.shop_id,
        )
        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load(recurring_order_id),
            "RecurringOrder",
        )
        ensure_related_to_shop(current_user, recurring_order.shop_id)
        logger.debug(
            "Loaded owned recurring order: "
            "recurring_order_id=%s shop_id=%s status=%s",
            recurring_order.id,
            recurring_order.shop_id,
            recurring_order.status,
        )
        return recurring_order

    async def load_owned_with_items(
        self,
        recurring_order_id: RecurringOrderId,
        current_user: CurrentUserDTO,
    ) -> RecurringOrder:
        logger.debug(
            "Loading owned recurring order with items: "
            "recurring_order_id=%s user_id=%s shop_id=%s",
            recurring_order_id,
            current_user.user_id,
            current_user.shop_id,
        )
        recurring_order = ensure_exists(
            await self._recurring_order_gateway.load_with_items(
                recurring_order_id
            ),
            "RecurringOrder",
        )
        ensure_related_to_shop(current_user, recurring_order.shop_id)
        logger.debug(
            "Loaded owned recurring order with items: "
            "recurring_order_id=%s shop_id=%s status=%s items_count=%d",
            recurring_order.id,
            recurring_order.shop_id,
            recurring_order.status,
            len(recurring_order.items),
        )
        return recurring_order
