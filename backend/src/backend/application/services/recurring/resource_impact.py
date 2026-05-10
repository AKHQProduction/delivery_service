import logging

from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import ensure_related_to_shop
from backend.application.vars import (
    ProductId,
    RecurringOrderStatus,
    TimeSlotId,
)
from backend.infrastructure.persistence.gateways import (
    RecurringOrderFilters,
    SQLAlchemyRecurringOrderGateway,
)

logger = logging.getLogger(__name__)


class RecurringOrderResourceImpact:
    def __init__(
        self,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
    ) -> None:
        self._recurring_order_gateway = recurring_order_gateway

    async def pause_for_deleted_product(
        self,
        product_id: ProductId,
        current_user: CurrentUserDTO,
    ) -> None:
        logger.info(
            "Checking recurring orders affected by deleted product: "
            "product_id=%s user_id=%s shop_id=%s",
            product_id,
            current_user.user_id,
            current_user.shop_id,
        )
        recurring_orders = await self._recurring_order_gateway.load_by_filters(
            RecurringOrderFilters(product_id=product_id)
        )
        for recurring_order in recurring_orders:
            ensure_related_to_shop(current_user, recurring_order.shop_id)
            recurring_order.status = RecurringOrderStatus.PAUSED
            logger.info(
                "Paused recurring order because product was deleted: "
                "recurring_order_id=%s product_id=%s",
                recurring_order.id,
                product_id,
            )
        logger.info(
            "Deleted product impact handled for recurring orders: "
            "product_id=%s affected=%d",
            product_id,
            len(recurring_orders),
        )

    async def pause_for_deleted_time_slot(
        self,
        time_slot_id: TimeSlotId,
        current_user: CurrentUserDTO,
    ) -> None:
        logger.info(
            "Checking recurring orders affected by deleted time slot: "
            "time_slot_id=%s user_id=%s shop_id=%s",
            time_slot_id,
            current_user.user_id,
            current_user.shop_id,
        )
        recurring_orders = await self._recurring_order_gateway.load_by_filters(
            RecurringOrderFilters(time_slot_id=time_slot_id)
        )
        for recurring_order in recurring_orders:
            ensure_related_to_shop(current_user, recurring_order.shop_id)
            recurring_order.status = RecurringOrderStatus.PAUSED
            recurring_order.time_slot_id = None
            logger.info(
                "Paused recurring order because time slot was deleted: "
                "recurring_order_id=%s time_slot_id=%s",
                recurring_order.id,
                time_slot_id,
            )
        logger.info(
            "Deleted time slot impact handled for recurring orders: "
            "time_slot_id=%s affected=%d",
            time_slot_id,
            len(recurring_orders),
        )
